#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Union, Optional, Dict
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from s3fs import S3FileSystem
import re

import json
from imageio import get_writer
import pandas as pd
from PIL import Image, ImageDraw
from shapely.geometry import Point, Polygon
import numpy as np

from .img import download_background_image
from ..constants import ALL_OBJECT_CLASSES, OBJECT_CLASSES_COLOR_MAP
from ..client import NuminaClient
from . import db
from .athena import query_tracks
from numina_admin_helpers import constants

###############################################################################


def separate_x_y_coords_into_single_columns(tracks: pd.DataFrame) -> pd.DataFrame:
    """
    Given a raw tracks dataframe, convert the string representation of a list into two
    columns of integer values.

    Parameters
    ----------
    tracks: pd.DataFrame
        The raw track data.
        See: athena.query_tracks

    Returns
    -------
    tracks: pd.DataFrame
        The same data but with an "x" and "y" column added that has the integer value
        for the bottom center column value.

    Notes
    -----
    This doesn't mutate the original, this returns a new dataframe.
    """
    # Create deep copy
    tracks = tracks.copy()

    # Add columns for the string x and string y
    tracks[["x", "y"]] = (
        tracks.bottom_center.str.strip("[]").str.split(",").values.tolist()
    )

    # Convert x and y columns to int
    tracks["x"] = tracks.x.astype(int)
    tracks["y"] = tracks.y.astype(int)

    return tracks


def get_start_and_end_per_track(tracks: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs a DataFrame of start and end details of all unique tracks in the
    provided dataframe.

    Parameters
    ----------
    tracks: pd.DataFrame
        The raw track data.
        See: athena.query_tracks

    Returns
    -------
    track_starts_and_ends: pd.DataFrame
        A dataframe with the start and end for each unique track.
    """
    # Per-track start datetime is just the minimum datetime
    # This will group by track id (each track snapshot is a row)
    # then find the index of the row with the minimum datetime for each group
    # Then pull those rows from the original tracks dataframe where index matches
    track_starts = tracks.loc[tracks.groupby(["trackid"]).time.idxmin()]

    # Per-track start datetime is just the maximum datetime
    # This will group by track id (each track snapshot is a row)
    # then find the index of the row with the maximum datetime for each group
    # Then pull those rows from the original tracks dataframe where index matches
    track_ends = tracks.loc[tracks.groupby(["trackid"]).time.idxmax()]

    # Merge these two sets of rows together
    starts_and_ends = track_starts.merge(
        track_ends,
        on="trackid",
        suffixes=("_start", "_end"),
    )

    # Clean up extra columns
    starts_and_ends = starts_and_ends.drop(["feedid_end", "class_end"], axis=1)
    starts_and_ends = starts_and_ends.rename(
        {
            "feedid_start": "feed_id",
            "class_start": "class",
        },
        axis=1,
    )

    return starts_and_ends


def point_in_zone(point: List[int], zone_demarcation: List[List[int]]) -> bool:
    """
    Check if the provided point is within the provided zone.

    Parameters
    ----------
    point: List[int]
        A list of integers in [x, y] order representing the point coordinates.
    zone_demarcation: List[List[int]]
        The list of points creating the zone boundary.

    Returns
    -------
    in_zone: bool
        Boolean representing whether or not the point is within the provided zone.
    """
    point = Point(point)
    zone = Polygon(zone_demarcation)

    return zone.contains(point)


def get_points_in_zone(
    tracks: pd.DataFrame,
    zone_demarcation: List[List[int]],
    point_x_col_name: str = "x",
    point_y_col_name: str = "y",
) -> pd.DataFrame:
    """
    Filter down track data to find the points in a provided zone.

    Parameters
    ----------
    tracks: pd.DataFrame
        The preprocessed track data.
        See: separate_x_y_coords_into_single_columns
    zone_demarcation: List[List[int]]
        The list of points creating the zone boundary.
    point_x_col_name: str
        The column name that contains the x coordinate for each point.
        Default: "x"
    point_y_col_name: str
        The column name that contains the y coordinate for each point.
        Default: "y"

    Returns
    -------
    in_zone_points: pd.DataFrame
        The filtered track data to only include points in the provided zone.
    """
    return tracks[
        tracks.apply(
            lambda row: point_in_zone(
                [row[point_x_col_name], row[point_y_col_name]],
                zone_demarcation,
            ),
            axis=1,
        )
    ]


def get_tracks_in_or_passed_through_zone(
    tracks: pd.DataFrame,
    zone_demarcation: List[List[int]],
    unique_track_id_col_name: str = "trackid",
    point_x_col_name: str = "x",
    point_y_col_name: str = "y",
) -> pd.DataFrame:
    """
    Filter down track data to any tracks that are wholly in or passed through
    the specified zone demarcation.

    Parameters
    ----------
    tracks: pd.DataFrame
        The preprocessed track data.
        See: separate_x_y_coords_into_single_columns
    zone_demarcation: List[List[int]]
        The list of points creating the zone boundary.
    unique_track_id_col_name: str
        The column name that contains the unique track id for each track.
        Default: "trackid"
    point_x_col_name: str
        The column name that contains the x coordinate for each point.
        Default: "x"
    point_y_col_name: str
        The column name that contains the y coordinate for each point.
        Default: "y"

    Returns
    -------
    tracks_in_zone: pd.DataFrame
        The filtered track data to only include tracks that are wholly in or which
        passed through the specified zone demarcation.
    """
    # Get points in zone then get their unique trackids then just subset original tracks
    # for any tracks with the matching track ids
    points_in_zone = get_points_in_zone(
        tracks=tracks,
        zone_demarcation=zone_demarcation,
        point_x_col_name=point_x_col_name,
        point_y_col_name=point_y_col_name,
    )

    # Get unique track ids
    unique_track_ids = points_in_zone[unique_track_id_col_name].unique()

    # Get subset of original where unique track id matches
    return tracks[tracks[unique_track_id_col_name].isin(unique_track_ids)]


def _process_track_replay(
    track_data: pd.DataFrame,
    save_path: Union[Path, str],
    fps: int,
    line_width: int,
    background_image_path: Optional[Union[Path, str]] = None,
    background_image_lut: Optional[Dict[pd.Timestamp, str]] = None,
    zone_demarcation: Optional[List[List[int]]] = None,
) -> Path:
    """
    Actual processing, visualization, and serialization function for
    track replays.

    In short this function will quickly generate a tree of frame-info needed for
    visualization, then iterate over the frames / datetimes and write individual
    frames of the replay at a time.

    This allows us to write massive track replays and keep memory cost low --
    while we will keep all visualization frame information and track data in memory,
    we only keep a single frame's pixel data in memory at a given time.
    """
    # Quickly iter through all track data and make a frame data tree
    # Top level keys are datetimes
    # their values are dictionaries that contain track id and a list of points sorted
    # by their index
    # i.e.
    # {
    #   "2021-04-09T11-00-00": {
    #       "some-track-a": {
    #           "obj_class": "pedestrian",
    #           "bounding_box": [x0, y0, x1, y1],
    #           "points": [(x0, y0), (x1, y1), (x_n, y_n)]
    #       },
    #       "some-track-b": {
    #           "obj_class": "bicycle",
    #           "bounding_box": [x0, y0, x1, y1],
    #           "points": [(x0, y0), (x_n, y_n)]
    #       },
    #   },
    #   ...
    # }

    if background_image_path is None and background_image_lut is None:
        raise ValueError(
            "Must provide one of `background_image_path` or `background_image_lut`"
        )

    # Group by timepoint and continuously keep track of which tracks
    # should be visualized at that timepoint
    frame_data = {}
    previous_frame_data = {}
    for dt, group in track_data.groupby("time"):
        # Construct new dict for this datetime / frame
        dt_str = dt.isoformat()
        frame_data[dt_str] = {}

        # Iter over group and add track info
        for track_id, points in group.groupby("trackid"):
            # There is only ever a single point for a unique track id
            # at any single timepoint
            point_details = points.iloc[0]

            # Handle appending prior track instance points to this frame
            # If the current track is in the previous frame
            # pull all its points into this frame as well
            if track_id in previous_frame_data:
                points = [
                    *previous_frame_data[track_id]["points"],
                    (int(point_details.x), int(point_details.y)),
                ]
            else:
                points = [(int(point_details.x), int(point_details.y))]

            # Add this tracks data to the frame set
            frame_data[dt_str][track_id] = {
                "obj_class": point_details["class"],
                "bounding_box": json.loads(point_details.box),
                "points": points,
            }

        # Update previous frame data
        previous_frame_data = frame_data[dt_str]

    # Iter and write frames
    with get_writer(save_path, mode="I", fps=fps) as writer:
        for i, dt in enumerate(track_data.time.sort_values(ascending=True)):
            dt_str = dt.isoformat()

            with TemporaryDirectory() as tmpdir:
                tmpdir = Path(tmpdir)

                # Load from LUT or from path
                if background_image_lut is not None:
                    fs = S3FileSystem()
                    if dt in background_image_lut:
                        background_image_path = str(tmpdir / "this-frame-bg.png")
                        fs.get(background_image_lut[dt], background_image_path)

                    else:
                        background_image_path = None

                # Load background image into PIL
                if background_image_path is not None:
                    with Image.open(background_image_path).convert("RGB") as img:
                        img_draw = ImageDraw.Draw(img)

                        # Optionally draw the zone demarcation
                        if zone_demarcation is not None:
                            img_draw.polygon(
                                zone_demarcation,
                                outline="#6ee263",  # light green
                            )

                        # Draw all tracks for this frame
                        for _, track_details in frame_data[dt_str].items():
                            img_draw.line(
                                xy=track_details["points"],
                                fill=OBJECT_CLASSES_COLOR_MAP[
                                    track_details["obj_class"]
                                ],
                                width=line_width,
                                joint="curve",
                            )
                            img_draw.rectangle(
                                xy=track_details["bounding_box"],
                                outline=OBJECT_CLASSES_COLOR_MAP[
                                    track_details["obj_class"]
                                ],
                                width=line_width,
                            )

                        # Write frame
                        writer.append_data(np.asarray(img))

    return save_path


def generate_track_replay(
    device_serial_no: str,
    start_time: Union[datetime, str],
    end_time: Union[datetime, str],
    save_path: Optional[Union[Path, str]] = None,
    background_image_path: Optional[Union[Path, str]] = None,
    base_serial_no: Optional[str] = None,
    zone_subset: Optional[Union[str, int]] = None,
    fps: int = 60,
    line_width: int = 3,
    obj_classes: List[str] = ALL_OBJECT_CLASSES,
    client: Optional[NuminaClient] = None,
) -> Path:
    """
    Generate a track replay.

    Parameters
    ----------
    device_serial_no: str
        A specific sensor serial number to query for.
        This is returned from `db.get_org_sensor_details`.
    start_time: Union[datetime, str]
        A start datetime to query the metrics against.
        If provided a string, ensure that the string is in isoformat.
    end_time: Union[datetime, str]
        An end datetime to query the metrics against.
        If provided a string, ensure that the string is in isoformat.
    save_path: Optional[Union[Path, str]]
        The path to where to save the produced file.
        Supported serialization formats:
        .gif, .mov, .avi, .mpg, .mpeg, .mp4, .mkv, .wmv
        Default: None (Save to current dir with filename generated based off params)
    background_image_path: Optional[Union[Path, str]]
        Path to a specific background image to use for the base of each frame.
        Useful when the device doesn't have a sample image
        (common in cases where the sensor was redeployed).
    base_serial_no: Optional[str]
        When generating a track replay for a previously decommissioned sensor
        the device serial number won't be the same as the data in athena.
        In which case, provide the serial number base to query athena for track data.
    zone_subset: Optional[Union[str, int]]
        An optional zone name or zone id that will be used to filter tracks to only
        those that were wholly in or which passed through the zone.
        If provided an id must be a zone id. If provided a string must be the zone name.
        Default: None (do not filter to zone)
    fps: int
        The frames per second to save the file with.
        We set this very high because each of our frames
        represents ~0.25 seconds of real time.
        Default: 60
    line_width: int
        The line width to use for each track.
        Default: 3px
    obj_classes: List[str]:
        The classes to count metrics for.
        Default: constants.ALL_OBJECT_CLASSES
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    save_path: Path
        The path of the produced file.

    Notes
    -----
    Must have ffmpeg installed to use.
    """
    # Get full device details
    device_details = db.get_device_by_serial_no(device_serial_no, client=client)

    # Convert times to datetime
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time)
    if isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time)

    # Construct save path if needed
    if save_path is None:
        # Handle zone save
        if zone_subset is None:
            zone_save_str = ""
        else:
            zone_save_str = f"-zone-{zone_subset}"
            zone_save_str = re.sub(r"[^0-9a-zA-Z]+", "-", zone_save_str)

        # Generate
        save_path = Path(
            f"track-replay-"
            f"{device_serial_no}{zone_save_str}-{'-'.join(obj_classes)}-"
            f"{start_time.isoformat()}-{end_time.isoformat()}.mp4"
        )

    # Select track data
    track_data = query_tracks(
        feed_id=device_details["feedId"],
        start_datetime=start_time,
        end_datetime=end_time,
        obj_classes=obj_classes,
    )

    # Add y and x columns
    track_data = separate_x_y_coords_into_single_columns(track_data)

    # Optionally zone subset
    if zone_subset is not None:
        # Get zone details
        sensor_zones = db.get_sensor_behavior_zones(
            device_serial_no=device_serial_no,
            client=client,
        )

        # Check that zone is available on this sensor
        if isinstance(zone_subset, int):
            matching_zones = sensor_zones[sensor_zones.zone_id == zone_subset]
        else:
            matching_zones = sensor_zones[sensor_zones.text == zone_subset]

        if len(matching_zones) == 0:
            raise ValueError(
                f"Could not find matching zone for sensor. "
                f"Zone: {zone_subset} -- Sensor: {device_serial_no}."
            )

        # Get single zone
        matching_zone = matching_zones.iloc[0]

        # Filter
        track_data = get_tracks_in_or_passed_through_zone(
            tracks=track_data,
            zone_demarcation=matching_zone.demarcation,
        )

        # Store demarcation for use in viz
        zone_demarcation = [tuple(point) for point in matching_zone.demarcation]

    else:
        # Default zone demarcation
        zone_demarcation = None

    # Catch empty frame
    if len(track_data) == 0:
        raise ValueError(
            "No tracks found for matching sensor, zone, and datetime subset."
        )

    # Download background image and generate track replay.
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Download background image
        if background_image_path is None:
            background_image_path = download_background_image(
                device_serial_no=device_serial_no,
                save_path=str(tmpdir / "sensor-bg.png"),
            )

        # Process and store track replay
        _process_track_replay(
            track_data=track_data,
            background_image_path=background_image_path,
            save_path=save_path,
            fps=fps,
            line_width=line_width,
            zone_demarcation=zone_demarcation,
        )

    return save_path


def generate_track_replay_from_available_frames(
    device_serial_no: str,
    start_time: Union[datetime, str],
    end_time: Optional[Union[datetime, str]] = None,
    real_duration: Optional[timedelta] = None,
    datetime_str_parse_format: Optional[str] = None,
    save_path: Optional[Union[str, Path]] = None,
    fps: int = 8,
    line_width: int = 3,
    obj_classes: List[str] = constants.ALL_OBJECT_CLASSES,
    client: Optional[NuminaClient] = None,
) -> Path:
    # Handle end time or real duration
    if end_time is None and real_duration is None:
        raise ValueError(
            "Must provide one of 'end_time' or 'real_duration' as a parameter."
        )

    if end_time is None and real_duration is not None:
        end_time = start_time + real_duration

    # Get full device details
    device_details = db.get_device_by_serial_no(device_serial_no, client=client)

    # Convert times to datetime
    if isinstance(start_time, str):
        if datetime_str_parse_format is None:
            start_time = datetime.fromisoformat(start_time)
        else:
            start_time = datetime.strptime(start_time, datetime_str_parse_format)
    if isinstance(end_time, str):
        if datetime_str_parse_format is None:
            end_time = datetime.fromisoformat(end_time)
        else:
            end_time = datetime.strptime(end_time, datetime_str_parse_format)

    # Construct save path if needed
    if save_path is None:
        # Generate
        save_path = Path(
            f"track-replay-"
            f"{device_serial_no}-{'-'.join(obj_classes)}-"
            f"{start_time.isoformat()}-{end_time.isoformat()}.mp4"
        )

    # Select track data
    track_data = query_tracks(
        feed_id=device_details["feedId"],
        start_datetime=start_time,
        end_datetime=end_time,
        obj_classes=obj_classes,
    )

    # Add y and x columns
    track_data = separate_x_y_coords_into_single_columns(track_data)

    # Catch empty frame
    if len(track_data) == 0:
        raise ValueError(
            "No tracks found for matching sensor, zone, and datetime subset."
        )

    # Find all frames that match timeframe
    fs = S3FileSystem()
    image_frames = {}
    current_datetime = start_time
    while current_datetime < end_time:
        current_datetime_str = current_datetime.strftime(r"%Y%m%d%H%M")
        glob_str = f"s3://numina-deid-images/{device_serial_no}/{current_datetime_str}*"

        # Only add frame if there is a matching datetime in the track data
        for image_frame in fs.glob(glob_str):
            image_frame_dt_portion = image_frame.split("/")[-1]
            detection_dt = pd.Timestamp(
                datetime.strptime(
                    image_frame_dt_portion.replace(".jpg", "")[:-3], r"%Y%m%d%H%M%S.%f"
                )
            )
            if (track_data.time == detection_dt).any():
                if detection_dt not in image_frames:
                    image_frames[detection_dt] = image_frame

        current_datetime += timedelta(seconds=1)

    _process_track_replay(
        track_data=track_data,
        background_image_lut=image_frames,
        save_path=save_path,
        fps=fps,
        line_width=line_width,
    )
