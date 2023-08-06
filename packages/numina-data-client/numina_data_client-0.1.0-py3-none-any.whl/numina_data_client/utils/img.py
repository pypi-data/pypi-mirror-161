#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

import cv2
import numpy as np
import pandas as pd
from PIL import Image
from matplotlib import pyplot as plt
from s3fs import S3FileSystem
from shapely.geometry import Polygon
from dateutil.tz import tzutc

from .. import constants, queries
from ..client import NuminaClient

###############################################################################

SAMPLE_IMAGE_FSTRING = constants.SAMPLE_IMAGE_BUCKET_AND_DIR + "{serial_no}.png"

###############################################################################


def download_background_image(
    device_serial_no: str,
    save_path: Optional[str] = None,
) -> str:
    """
    Downloads a sensor sample image and returns the save path.

    Parameters
    ----------
    device_serial_no: str
        The serial number for the sensor to pull a sample image for.
    save_path: Optional[str]
        A specific path to save the file to.
        Default: {cwd}/{device_sensor_no}.png

    Returns
    -------
    save_path: str
        The ultimate save path for where the image was saved to.
    """
    # Construct save path for image
    if save_path is None:
        save_path = f"{device_serial_no}.png"

    # Download file
    fs = S3FileSystem()
    fs.get(
        SAMPLE_IMAGE_FSTRING.format(serial_no=device_serial_no),
        save_path,
    )

    return save_path


def overlay_origin_and_terminus_points_on_sample_image(
    background_image_path: str,
    data: pd.DataFrame,
    save_path: str = "points-overlaid-image.png",
    origin_point_color: str = "green",
    origin_point_alpha: float = 0.5,
    origin_point_marker: str = ".",
    terminus_point_color: str = "red",
    terminus_point_alpha: float = 0.5,
    terminus_point_marker: str = ".",
    zone_demarcation: Optional[List[List[int]]] = None,
    zone_demarcation_boundary_color: str = "black",
    zone_demarcation_line_width: float = 3.0,
    zone_demarcation_line_style: str = "dotted",
) -> str:
    """
    Overlays the origin and terminus points found in the provided data on top of the
    background image.

    Parameters
    ----------
    background_image_path: str
        The path to the background image to overlay points over.
        From download_background_image.
    data: pd.DataFrame
        The origin and terminus point track data.
        In general this data comes from athena.query_tracks,
        which is then processed by tracks.separate_x_y_coords_into_single_columns,
        then finally processed by tracks.get_start_and_end_per_track.
    save_path: str
        The path to save the figure at.
    *_point_color: str
        The point color for the assoicated origin or terminus point.
        Allowed colors: https://matplotlib.org/3.1.0/gallery/color/named_colors.html
        More: https://matplotlib.org/3.1.0/tutorials/colors/colors.html#xkcd-colors
    *_point_alpha: float
        The alpha value for the associated origin or terminus point.
        This is important if you you think there will be heavy or light clustering of
        points. I.E. if heavy cluster, it is likely best to lower the alpha value.
    *_marker: str
        The marker for the associated origin or terminus point.
        Allowed markers: https://matplotlib.org/3.1.1/api/markers_api.html
    zone_demarcation: Optional[List[List[int]]]
        An optional zone demarcation to plot as a boundary on the image.
    zone_demarcation_boundary_color: str
        The color for the zone demarcation boundary to be drawn with.
        Default: "black"
    zone_demarcation_line_width: float
        The line width for the zone demarcation boundary to be drawn with.
        Default: 3.0
    zone_demarcation_line_style: str
        The line style for the zone demarcation boundary to be drawn with.
        Default: "dotted"
        Allowed styles:
        https://matplotlib.org/3.1.0/gallery/lines_bars_and_markers/linestyles.html

    Returns
    -------
    image_path: str
        The resulting image path.
    """
    # Clear any existing plots
    plt.clf()

    # Read background image
    
    bg_img = Image.open(background_image_path)

    # Show the image on the plot
    fig, ax = plt.subplots(1)
    ax.imshow(bg_img)

    # Display the origin and terminus points
    plt.scatter(
        data.x_start,
        data.y_start,
        color=origin_point_color,
        alpha=origin_point_alpha,
        marker=origin_point_marker,
    )
    plt.scatter(
        data.x_end,
        data.y_end,
        color=terminus_point_color,
        alpha=terminus_point_alpha,
        marker=terminus_point_marker,
    )

    # Add optional zone demarcation
    if zone_demarcation is not None:
        zone = Polygon(zone_demarcation)
        zone_x, zone_y = zone.exterior.xy
        ax.plot(
            zone_x,
            zone_y,
            color=zone_demarcation_boundary_color,
            linewidth=zone_demarcation_line_width,
            linestyle=zone_demarcation_line_style,
            zorder=2,
            solid_capstyle="round",
        )

    # Remove axis
    plt.axis("off")

    # Save
    plt.savefig(save_path, bbox_inches="tight", transparent=True, pad_inches=0)

    return save_path


def overlay_zone_on_sample_image(
    background_image_path: str,
    zone_demarcation: Union[List[List[int]], List[List[List[int]]]],
    save_path: str = "zone-overlaid-image.png",
    zone_fill_color: Union[str, List[str]] = "lightgreen",
    zone_fill_alpha: Union[float, List[float]] = 0.5,
    zone_demarcation_boundary_color: Union[str, List[str]] = "green",
    zone_demarcation_line_width: Union[float, List[float]] = 1.0,
    zone_demarcation_line_style: Union[str, List[str]] = "dotted",
) -> str:
    """
    Overlays a zone onto a background image.

    Parameters
    ----------
    background_image_path: str
        The path to the background image to overlay points over.
        From download_background_image.
    zone_demarcation: Union[List[List[int]], List[List[List[int]]]]
        An zone demarcation to plot as a boundary on the image.
    save_path: str
        The path to save the figure at.
    zone_fill_color: Union[str, List[str]]
        The color to fill the zone with.
        Default: lightgreen
        Allowed colors: https://matplotlib.org/3.1.0/gallery/color/named_colors.html
        More: https://matplotlib.org/3.1.0/tutorials/colors/colors.html#xkcd-colors
    zone_fill_alpha: Union[float, List[float]]
        The alpha value for the zone fill.
    zone_demarcation_boundary_color: Union[str, List[str]]
        The color for the zone demarcation boundary to be drawn with.
        Default: "green"
    zone_demarcation_line_width: Union[float, List[float]]
        The line width for the zone demarcation boundary to be drawn with.
        Default: 1.0
    zone_demarcation_line_style: Union[str, List[str]]
        The line style for the zone demarcation boundary to be drawn with.
        Default: "dotted"
        Allowed styles:
        https://matplotlib.org/3.1.0/gallery/lines_bars_and_markers/linestyles.html

    Returns
    -------
    image_path: str
        The resulting image path.
    """
    # Check parameters for "many zones"
    if isinstance(zone_fill_color, list):
        # Check that all params are matching len
        if not all(
            len(param) == len(zone_demarcation)
            for param in [
                zone_fill_color,
                zone_fill_alpha,
                zone_demarcation_boundary_color,
                zone_demarcation_line_width,
                zone_demarcation_line_style,
            ]
        ):
            raise ValueError(
                "If providing a list of zones to process all zone demarcation and "
                "styling options must be the same length. "
                "I.e. When providing two zones, "
                "you must also provide two colors and line styles, etc."
            )

    # Not using many
    else:
        # Just wrap in lists
        zone_demarcation = [zone_demarcation]
        zone_fill_color = [zone_fill_color]
        zone_fill_alpha = [zone_fill_alpha]
        zone_demarcation_boundary_color = [zone_demarcation_boundary_color]
        zone_demarcation_line_width = [zone_demarcation_line_width]
        zone_demarcation_line_style = [zone_demarcation_line_style]

    # Read background image
    bg_img = Image.open(background_image_path)

    # Normalize to 3d RGB
    if len(bg_img.shape) == 2:
        bg_img = cv2.cvtColor(bg_img, cv2.COLOR_GRAY2BGR)

    # Show the image on the plot
    fig, ax = plt.subplots(1)
    ax.imshow(bg_img)

    # Add zone fill and boundary
    for i in range(len(zone_demarcation)):
        zone = Polygon(zone_demarcation[i])
        zone_x, zone_y = zone.exterior.xy
        ax.fill(
            zone_x,
            zone_y,
            color=zone_fill_color[i],
            alpha=zone_fill_alpha[i],
        )
        ax.plot(
            zone_x,
            zone_y,
            color=zone_demarcation_boundary_color[i],
            linewidth=zone_demarcation_line_width[i],
            linestyle=zone_demarcation_line_style[i],
            zorder=i + 1,
            solid_capstyle="round",
        )

    # Remove axis
    plt.axis("off")

    # Save
    plt.savefig(save_path, bbox_inches="tight", transparent=True, pad_inches=0)

    return save_path


def get_zone_heatmap(
    device_serial_no: str,
    zone_id: int,
    obj_class: str,
    start_datetime: Union[str, datetime],
    end_datetime: Union[str, datetime],
    local_timezone: str,
    save_path: Optional[Union[str, Path]] = None,
    numina_client: Optional[NuminaClient] = None,
) -> str:
    """
    Create a heatmap image for a specific zone and object class.

    Parameters
    ----------
    device_serial_no: str
        The serial number for the sensor to pull a sample image for.
    zone_id: int
        The specific zone id to retrieve heatmap data for.
    obj_class: str
        The specific object class to retrieve heatmap data for.
    start_datetime: Union[str, datetime]
        The start datetime to retrieve heatmap data for.
    end_datetime: Union[str, datetime]
        The end datetime to retrive heatmap data for.
    local_timezone: str
        The sensor local timezone.
    save_path: Optional[Union[str, Path]]
        A specific save path to save the produced heatmap to.
        Default: {cwd}/{device_serial_no}-{zone_id}-{obj_class}-heatmap.png
    numina_client: Optional[NuminaClient]
        An optional existing client to use for querying.
        Default: None (create new client)

    Returns
    -------
    zone_heatmap_path: str
        The resulting image save path.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Download and read sample image
        sensor_sample_img_path = download_background_image(
            device_serial_no=device_serial_no,
            save_path=f"{tmp_dir}/sensor-bg-image.png",
        )
        base_image = Image.open(sensor_sample_img_path)

        # Convert datetimes
        if isinstance(start_datetime, datetime):
            start_datetime = start_datetime.isoformat()
        if isinstance(end_datetime, datetime):
            end_datetime = end_datetime.isoformat()

        # Get zone heatmap from API
        if numina_client is None:
            numina_client = NuminaClient()

        heatmap_result = numina_client.execute(
            queries.ZONE_HEATMAP.format(
                zone_id=zone_id,
                obj_class=obj_class,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                timezone=local_timezone,
            ).replace("'", '"')
        )

        # Pull heatmap data from API result
        heatmap_data = heatmap_result["zoneHeatmaps"]["edges"][0]["node"]["heatmap"]

        # Covert to numpy array
        heatmap = np.zeros((480, 640))
        for x, y, v in heatmap_data:
            heatmap[y, x] = v * 255

        # Cast to uint8 as we multiplied by 255
        heatmap = heatmap.astype(np.uint8)

        # Convert to colormap (i.e. larger values are more blue)
        colormap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        # Blend the colormap onto the sensor sample image
        # Where the heatmap is greater than 0 in each sample (RGB / BGR) dimension
        # mult the alpha by the colormap value and merge with sensor sample image value
        alpha = 0.5
        # Normalize base image to RGB
        if len(base_image.shape) == 2:
            base_image = cv2.cvtColor(base_image, cv2.COLOR_GRAY2BGR)
        for sample_dim_index in range(3):
            base_image[heatmap > 0, sample_dim_index] = (
                alpha * colormap[heatmap > 0, sample_dim_index]
            ) + ((1 - alpha) * base_image[heatmap > 0, 0])

        # Covert BRG to RGB (i.e. larger values now map to more red)
        base_image = cv2.cvtColor(base_image, cv2.COLOR_BGR2RGB)

        # Determine save path
        if save_path is None:
            save_path = f"{device_serial_no}-{zone_id}-{obj_class}-heatmap.png"

        # Save image
        Image.save(save_path, base_image)

        return save_path


def get_feed_heatmap(
    device_serial_no: str,
    obj_class: str,
    start_datetime: Union[str, datetime],
    end_datetime: Union[str, datetime],
    local_timezone: str,
    save_path: Optional[Union[str, Path]] = None,
    numina_client: Optional[NuminaClient] = None,
) -> str:
    """
    Create a heatmap image for a sensor and object class.

    Parameters
    ----------
    device_serial_no: str
        The serial number for the sensor to pull a sample image for.
    obj_class: str
        The specific object class to retrieve heatmap data for.
    start_datetime: Union[str, datetime]
        The start datetime to retrieve heatmap data for.
    end_datetime: Union[str, datetime]
        The end datetime to retrive heatmap data for.
    local_timezone: str
        The sensor local timezone.
    save_path: Optional[Union[str, Path]]
        A specific save path to save the produced heatmap to.
        Default: {cwd}/{device_serial_no}-{obj_class}-heatmap.png
    numina_client: Optional[NuminaClient]
        An optional existing client to use for querying.
        Default: None (create new client)

    Returns
    -------
    zone_heatmap_path: str
        The resulting image save path.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Download and read sample image
        sensor_sample_img_path = download_background_image(
            device_serial_no=device_serial_no,
            save_path=f"{tmp_dir}/sensor-bg-image.png",
        )
        base_image = Image.open(sensor_sample_img_path)

        # Convert datetimes
        if isinstance(start_datetime, datetime):
            start_datetime = start_datetime.isoformat()
        if isinstance(end_datetime, datetime):
            end_datetime = end_datetime.isoformat()

        # Get zone heatmap from API
        if numina_client is None:
            numina_client = NuminaClient()

        heatmap_result = numina_client.execute(
            queries.FEED_HEATMAP.format(
                serial_no=device_serial_no,
                obj_class=obj_class,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                timezone=local_timezone,
            ).replace("'", '"')
        )

        # Pull heatmap data from API result
        heatmap_data = heatmap_result["feedHeatmaps"]["edges"][0]["node"]["heatmap"]

        # Covert to numpy array
        heatmap = np.zeros((480, 640))
        for x, y, v in heatmap_data:
            heatmap[y, x] = v * 255

        # Cast to uint8 as we multiplied by 255
        heatmap = heatmap.astype(np.uint8)

        # Convert to colormap (i.e. larger values are more blue)
        colormap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        # Blend the colormap onto the sensor sample image
        # Where the heatmap is greater than 0 in each sample (RGB / BGR) dimension
        # mult the alpha by the colormap value and merge with sensor sample image value
        alpha = 0.5
        for sample_dim_index in range(3):
            base_image[heatmap > 0, sample_dim_index] = (
                alpha * colormap[heatmap > 0, sample_dim_index]
            ) + ((1 - alpha) * base_image[heatmap > 0, 0])

        # Covert BRG to RGB (i.e. larger values now map to more red)
        base_image = cv2.cvtColor(base_image, cv2.COLOR_BGR2RGB)

        # Determine save path
        if save_path is None:
            save_path = f"{device_serial_no}-{obj_class}-heatmap.png"

        # Save image
        Image.save(save_path, base_image)

        return save_path

