#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ..client import NuminaClient
from .. import queries, mutations
from ..constants import ALL_OBJECT_CLASSES, CommonIntervals

###############################################################################


def get_org_details(
    org_alias: str,
    client: Optional[NuminaClient] = None,
) -> Optional[Dict[str, Any]]:
    """
    Get the full organization details from just the organization alias.

    Parameters
    ----------
    org_alias: str
        The organization short name to get the full details for.
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    org_details: Optional[Dict[str, Any]]
        The full details for the organization.
        If org wasn't found returns None.
    """
    # Create client if none provided
    if client is None:
        client = NuminaClient()

    # Get details from alias
    org_details = client.execute(
        queries.GET_ORG_DETAILS_BY_ALIAS.format(organization_alias=org_alias)
    )

    # Org exists, return
    if len(org_details["organizations"]["edges"]) > 0:
        return org_details["organizations"]["edges"][0]["node"]

    # Org doesn't exist, return None
    return None


def get_all_orgs(
    client: Optional[NuminaClient] = None,
) -> pd.DataFrame:
    """
    Get all organization details.

    Parameters
    ----------
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    orgs: pd.DataFrame
        A dataframe of all organization details.
    """
    # Create client if none provided
    if client is None:
        client = NuminaClient()

    orgs = client.execute(queries.GET_ALL_ORGS)

    parsed = []
    nodes = orgs["organizations"]["edges"]
    for node in nodes:
        parsed.append(node["node"])

    return pd.DataFrame(parsed)


def get_org_sensor_details(
    org_name: str = None,
    org_alias: str = None,
    client: Optional[NuminaClient] = None,
) -> pd.DataFrame:
    """
    Get and return all sensors for an org as a dataframe.

    Parameters
    ----------
    org_name: str
        The organization name to get sensor details for.
        Must provide either the org name or the org alias.
        Example: Exploratorium
    org_alias: str
        The organization short name to get sensor details for.
        Must provide either the org name or the org alias.
        Example: exp
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    sensors: pd.DataFrame
        All sensors and their details for an organization.

    Raises
    ------
    ValueError
        No organization found with provided name or alias.
    """
    # Check that org name or alias was provided
    if org_name is None and org_alias is None:
        raise ValueError("Must provide either org_name or org_alias.")

    # Create client if none provided
    if client is None:
        client = NuminaClient()

    # Use org name
    if org_name is not None:
        org_and_all_devices_details = client.execute(
            queries.SINGLE_ORG_ALL_SENSORS_FROM_ORG_NAME.format(
                organization_name=org_name
            )
        )

    # Use org alias
    elif org_alias is not None:
        org_and_all_devices_details = client.execute(
            queries.SINGLE_ORG_ALL_SENSORS_FROM_ORG_ALIAS.format(
                organization_alias=org_alias
            )
        )

    # Reduce by getting single organization
    if len(org_and_all_devices_details["organizations"]["edges"]) > 0:
        org_and_all_devices_details = org_and_all_devices_details["organizations"][
            "edges"
        ][0]["node"]
    else:
        raise ValueError("No organization found for provided parameters")

    # Unpack
    org_id = org_and_all_devices_details["rawId"]
    org_name = org_and_all_devices_details["name"]
    org_alias = org_and_all_devices_details["alias"]
    org_timezone = org_and_all_devices_details["timezone"]
    devices = org_and_all_devices_details["devices"]["edges"]

    # Create basic device details
    org_devices = []
    for device in devices:
        org_devices.append(
            {
                "organization_id": org_id,
                "organization_name": org_name,
                "organization_alias": org_alias,
                "organization_timezone": org_timezone,
                **device["node"],
            }
        )

    return pd.DataFrame(org_devices)


def get_sensor_behavior_zones(
    device_serial_no: str,
    client: Optional[NuminaClient] = None,
) -> pd.DataFrame:
    """
    Get all behavior zones for a single sensor.

    Parameters
    ----------
    device_serial_no: str
        The device serial number to get behavior zones for.
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    zones: pd.DataFrame
        The behavior zones attached to this device.
    """
    # Create client if none provided
    if client is None:
        client = NuminaClient()

    # Get behavior zones for the device
    sensor_and_all_bz_details = client.execute(
        queries.BEHAVIOR_ZONES_FROM_DEVICE_SERIAL_NOS.format(
            serial_nos=[device_serial_no]
        ).replace("'", '"')
    )

    # Unpack
    bzs = []
    for bz in sensor_and_all_bz_details["behaviorZones"]["edges"]:
        bzs.append(
            {
                "device_serial_no": device_serial_no,
                **bz["node"],
            }
        )

    return pd.DataFrame(bzs)


def get_zone_count_metrics(
    zone_id: int,
    start_time: Union[datetime, str],
    end_time: Union[datetime, str],
    timezone: str,
    interval: str = CommonIntervals.OneHour,
    obj_classes: List[str] = ALL_OBJECT_CLASSES,
    client: Optional[NuminaClient] = None,
) -> pd.DataFrame:
    """
    Get per-interval zone count metrics for each object class.

    Parameters
    ----------
    zone_id: int
        A specific zone id to query for.
        This is returned with `get_sensor_behavior_zones`.
    start_time: Union[datetime, str]
        A start datetime to query the metrics against.
        If provided a string, ensure that the string is in isoformat.
    end_time: Union[datetime, str]
        An end datetime to query the metrics against.
        If provided a string, ensure that the string is in isoformat.
    timezone: str
        The timezone you want the metrics to be queried against.
        Recommended to query with the sensor / organization timezone which is returned
        with `get_org_sensor_details`.
    interval: str
        A string representation of the interval at which to count metrics.
        See constants.CommonIntervals for examples.
        Default: "1h"
    obj_classes: List[str]:
        The classes to count metrics for.
        Default: constants.ALL_OBJECT_CLASSES
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    zone_count_metrics: pd.DataFrame
        A dataframe where each row is a sum of the unique instances of an object class
        for the specified interval.
        I.E. If provided obj_classes of ["pedestrian"] and an interval of "1h", each
        row would be a different interval of pedestrians with the count of unique
        pedestrians in the zone for that hour.
    """
    # Create client if none provided
    if client is None:
        client = NuminaClient()

    # Convert times to str
    if isinstance(start_time, datetime):
        start_time = start_time.isoformat()
    if isinstance(end_time, datetime):
        end_time = end_time.isoformat()

    # We run these one at a time because large queries tend to time out
    # After running one at a time we concat all frames into single
    obj_class_results = []
    for obj_class in obj_classes:
        # Run query
        obj_class_results.append(
            client.execute(
                queries.ZONE_COUNT_METRICS.format(
                    zone_ids=[zone_id],
                    start_time=start_time,
                    end_time=end_time,
                    interval=interval,
                    obj_classes=[obj_class],
                    timezone=timezone,
                ).replace("'", '"')
            )
        )

    # Convert to frame
    all_count_metrics = []
    for obj_class_result in obj_class_results:
        count_metrics = []
        for count_metric in obj_class_result["zoneCountMetrics"]["edges"]:
            count_metrics.append(
                {
                    "zone_id": zone_id,
                    **count_metric["node"],
                }
            )

        all_count_metrics.append(count_metrics)

    # Create dataframes of all count metrics
    all_count_metrics = [
        pd.DataFrame(count_metrics) for count_metrics in all_count_metrics
    ]

    return pd.concat(all_count_metrics).reset_index(drop=True)


def get_feed_count_metrics(
    device_serial_no: str,
    start_time: Union[datetime, str],
    end_time: Union[datetime, str],
    timezone: str,
    interval: str = CommonIntervals.OneHour,
    obj_classes: List[str] = ALL_OBJECT_CLASSES,
    client: Optional[NuminaClient] = None,
) -> pd.DataFrame:
    """
    Get per-interval feed count metrics for each object class.

    Parameters
    ----------
    device_serial_no: int
        A specific device serial number to query for.
        This is returned with `get_org_sensor_details`.
    start_time: Union[datetime, str]
        A start datetime to query the metrics against.
        If provided a string, ensure that the string is in isoformat.
    end_time: Union[datetime, str]
        An end datetime to query the metrics against.
        If provided a string, ensure that the string is in isoformat.
    timezone: str
        The timezone you want the metrics to be queried against.
        Recommended to query with the sensor / organization timezone which is returned
        with `get_org_sensor_details`.
    interval: str
        A string representation of the interval at which to count metrics.
        See constants.CommonIntervals for examples.
        Default: "1d"
    obj_classes: List[str]:
        The classes to count metrics for.
        Default: constants.ALL_OBJECT_CLASSES
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    feed_count_metrics: pd.DataFrame
        A dataframe where each row is a sum of the unique instances of an object class
        for the specified interval.
        I.E. If provided obj_classes of ["pedestrian"] and an interval of "1h", each
        row would be a different interval of pedestrians with the count of unique
        pedestrians in the feed for that hour.
    """
    # Create client if none provided
    if client is None:
        client = NuminaClient()

    # Convert times to str
    if isinstance(start_time, datetime):
        start_time = start_time.isoformat()
    if isinstance(end_time, datetime):
        end_time = end_time.isoformat()

    # We run these one at a time because large queries tend to time out
    # After running one at a time we concat all frames into single
    obj_class_results = []
    for obj_class in obj_classes:
        # Run query
        obj_class_results.append(
            client.execute(
                queries.FEED_COUNT_METRICS.format(
                    serial_nos=[device_serial_no],
                    start_time=start_time,
                    end_time=end_time,
                    interval=interval,
                    obj_classes=[obj_class],
                    timezone=timezone,
                ).replace("'", '"')
            )
        )

    # Convert to frame
    all_count_metrics = []
    for obj_class_result in obj_class_results:
        count_metrics = []
        for count_metric in obj_class_result["feedCountMetrics"]["edges"]:
            count_metrics.append(
                {
                    "device_serial_no": device_serial_no,
                    **count_metric["node"],
                }
            )

        all_count_metrics.append(count_metrics)

    # Create dataframes of all count metrics
    all_count_metrics = [
        pd.DataFrame(count_metrics) for count_metrics in all_count_metrics
    ]

    return pd.concat(all_count_metrics).reset_index(drop=True)


def get_max_occupancy(
    device_serial_no: str,
    start_time: Union[datetime, str],
    end_time: Union[datetime, str],
    timezone: str,
    interval: str = CommonIntervals.OneHour,
    obj_classes: List[str] = ALL_OBJECT_CLASSES,
    client: Optional[NuminaClient] = None,
) -> pd.DataFrame:
    """
    Get per-interval feed max occupancy metrics for all object classes in a single
    sensor view.

    Parameters
    ----------
    device_serial_no: int
        A specific device serial number to query for.
        This is returned with `get_org_sensor_details`.
    start_time: Union[datetime, str]
        A start datetime to query the metrics against.
        If provided a string, ensure that the string is in isoformat.
    end_time: Union[datetime, str]
        An end datetime to query the metrics against.
        If provided a string, ensure that the string is in isoformat.
    timezone: str
        The timezone you want the metrics to be queried against.
        Recommended to query with the sensor / organization timezone which is returned
        with `get_org_sensor_details`.
    interval: str
        A string representation of the interval at which to count metrics.
        See constants.CommonIntervals for examples.
        Default: "1d"
    obj_classes: List[str]:
        The classes to count metrics for.
        Default: constants.ALL_OBJECT_CLASSES
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    feed_occupancy_metrics: pd.DataFrame
        A dataframe where each row is the max of the unique instances of an object class
        for the specified interval.
        I.E. If provided obj_classes of ["pedestrian"] and an interval of "1h", each
        row would be a different interval of pedestrians with the peak number of unique
        pedestrians in the feed for that hour.
    """
    # Create client if none provided
    if client is None:
        client = NuminaClient()

    # Convert times to str
    if isinstance(start_time, datetime):
        start_time = start_time.isoformat()
    if isinstance(end_time, datetime):
        end_time = end_time.isoformat()

    # We run these one at a time because large queries tend to time out
    # After running one at a time we concat all frames into single
    obj_class_results = []
    for obj_class in obj_classes:
        # Run query
        obj_class_results.append(
            client.execute(
                queries.MAX_OCCUPANCY.format(
                    serial_nos=[device_serial_no],
                    start_time=start_time,
                    end_time=end_time,
                    interval=interval,
                    obj_classes=[obj_class],
                    timezone=timezone,
                ).replace("'", '"')
            )
        )

    # Convert to frame
    all_occupancy_metrics = []
    for obj_class_result in obj_class_results:
        occupancy_metrics = []
        for count_metric in obj_class_result["maxOccupancy"]["edges"]:
            occupancy_metrics.append(
                {
                    "device_serial_no": device_serial_no,
                    **count_metric["node"],
                }
            )

        all_occupancy_metrics.append(occupancy_metrics)

    # Create dataframes of all count metrics
    all_occupancy_metrics = [
        pd.DataFrame(count_metrics) for count_metrics in all_occupancy_metrics
    ]

    return pd.concat(all_occupancy_metrics).reset_index(drop=True)


def get_zone_dwell_time_distribution(
    zone_id: int,
    start_datetime: Union[datetime, str],
    end_datetime: Union[datetime, str],
    timezone: str,
    interval: str = CommonIntervals.OneHour,
    obj_classes: List[str] = ALL_OBJECT_CLASSES,
    datetime_split_intervals: int = 1,
    client: Optional[NuminaClient] = None,
) -> pd.DataFrame:
    """
    Get dwell time distribution metrics for a zone over a time period.

    Parameters
    ----------
    zone_id: int
        The database id for the zone to get metrics for.
    start_datetime: Union[datetime, str]
        A start datetime to query the metrics against.
        If provided a string, ensure that the string is in isoformat.
    end_datetime: Union[datetime, str]
        An end datetime to query the metrics against.
        If provided a string, ensure that the string is in isoformat.
    timezone: str
        The timezone you want the metrics to be queried against.
        Recommended to query with the sensor / organization timezone which is returned
        with `get_org_sensor_details`.
    interval: str
        A string representation of the interval at which to count metrics.
        See constants.CommonIntervals for examples.
        Default: "1d"
    obj_classes: List[str]:
        The classes to count metrics for.
        Default: constants.ALL_OBJECT_CLASSES
    datetime_split_intervals: int
        How many intervals the provided datetime range should be split into for
        data retrieval.
        Default: 1 (do not split)
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    zone_dwell_dist: pd.DataFrame
        A dataframe with zone dwell time metrics (mean, percentiles, counts, etc) for
        the time period specified.
    """
    # Create client if none provided
    if client is None:
        client = NuminaClient()

    # Parse datetimes if needed
    if isinstance(start_datetime, str):
        start_datetime = datetime.fromisoformat(start_datetime)
    if isinstance(end_datetime, str):
        end_datetime = datetime.fromisoformat(end_datetime)

    # If desired, split date ranges into multiple intervals
    # to make requesting the data actually possible
    if datetime_split_intervals > 1:
        diff = (end_datetime - start_datetime) / datetime_split_intervals
        datetime_ranges = []
        for i in range(datetime_split_intervals):
            datetime_ranges.append(
                (
                    start_datetime + (diff * i),
                    start_datetime + (diff * (i + 1)),
                )
            )
    else:
        datetime_ranges = [(start_datetime, end_datetime)]

    # We run these one at a time because large queries tend to time out
    # After running one at a time we concat all frames into single
    partitions = []
    for obj_class in obj_classes:
        for start_dt, end_dt in datetime_ranges:
            # Convert times to str:
            start_dt = start_dt.isoformat()
            end_dt = end_dt.isoformat()

            # Run query
            partitions.append(
                client.execute(
                    queries.ZONE_DWELL_TIME.format(
                        zone_id=zone_id,
                        start_datetime=start_dt,
                        end_datetime=end_dt,
                        obj_classes=[obj_class],
                        timezone=timezone,
                        interval=interval,
                    ).replace("'", '"')
                )
            )

    # Convert to frame
    all_distributions = []
    for partition in partitions:
        distro_metrics = []
        for distro_metric in partition["zoneDwellTimeDistribution"]["edges"]:
            distro_metrics.append(
                {
                    "zone_id": zone_id,
                    **distro_metric["node"],
                }
            )

        all_distributions.append(distro_metrics)

    # Create dataframes of all count metrics
    all_distributions = [
        pd.DataFrame(count_metrics) for count_metrics in all_distributions
    ]

    # Concat into single frame
    zone_dwell = pd.concat(all_distributions).reset_index(drop=True)

    # Fix datetimes
    zone_dwell["datetime"] = zone_dwell.time.apply(lambda x: x[:-6])
    zone_dwell["datetime"] = pd.to_datetime(zone_dwell["datetime"])
    zone_dwell["time"] = zone_dwell["datetime"].dt.time

    today = datetime.now().date()
    zone_dwell["time_as_dt"] = zone_dwell.time.apply(
        lambda x: datetime.combine(today, x)
    )

    return zone_dwell


def create_device_with_location(
    org_id: str,
    device_serial_no: str,
    device_alias: str,
    device_name: str,
    device_lat: float,
    device_long: float,
    device_azimuth: int,
    client: Optional[NuminaClient] = None,
) -> Dict[str, Any]:
    """
    Create a new device for an organization.

    Parameters
    ----------
    org_id: str
        The database ID for the organization to add the device to.
    device_serial_no: str
        The serial number for the device.
    device_alias: str
        An optional specific alias to attach to the device.
    device_name: str
        A name for the device.
    device_lat: float
        The latitudinal coordinate for the device.
    device_long: float
        The longitudinal coordinate for the device.
    device_azimuth: int
        The heading of the device.
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    device_details: Dict[str, Any]
        The created device short details.

    Raises
    ------
    gql.transport.exceptions.TransportQueryError
        Device already found in database.
    """
    # Create client if none provided
    if client is None:
        client = NuminaClient()

    # Create device
    device = client.execute(
        mutations.CREATE_DEVICE_WITH_LOCATION.format(
            organization_id=org_id,
            device_serial_no=device_serial_no,
            device_alias=device_alias,
            device_name=device_name,
            device_lat=device_lat,
            device_long=device_long,
            device_azimuth=device_azimuth,
        )
    )

    return device["installSensor"]["device"]


def create_behavior_zone(
    device_serial_no: str,
    text: str,
    demarcation: List[List[int]],
    color: str = "red",
    client: Optional[NuminaClient] = None,
) -> Dict[str, Any]:
    """
    Create a behavior zone for a sensor.

    Parameters
    ----------
    device_serial_no: str
        The serial number for the sensor to create a zone for.
    text: str
        The text (name) to attach to this zone.
    demarcation: List[List[int]]
        A list of [x, y] int point values to act as the zone boundary.
    color: str
        A color to use for displaying the zone in the web UI.
        Default: "red"
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    zone_details: Dict[str, Any]
        The created zone details.
    """
    # Create client if none provided
    if client is None:
        client = NuminaClient()

    # Create behavior zone for the device
    bz = client.execute(
        mutations.CREATE_BEHAVIOR_ZONE.format(
            serial_no=device_serial_no,
            text=text,
            demarcation=demarcation,
            color=color,
        )
    )

    return bz["createBehaviorZone"]["behaviorZone"]


def delete_behavior_zone(
    zone_id: int,
    client: Optional[NuminaClient] = None,
) -> Dict[str, int]:
    """
    Delete a behavior zone.

    Parameters
    ----------
    zone_id: int
        The raw id for the zone to delete.
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    success: Dict[str, int]
        Status for the operation.
        If success with return a key "success" with the value of the zone id that was
        deleted.
    """
    # Create client if none provided
    if client is None:
        client = NuminaClient()

    # Delete behavior zones for the device
    return client.execute(mutations.DELETE_BEHAVIOR_ZONE.format(zone_id=zone_id))[
        "deleteBehaviorZone"
    ]


def get_device_by_serial_no(
    device_serial_no: str,
    client: Optional[NuminaClient] = None,
) -> Optional[Dict[str, Any]]:
    """
    Get a device's full information from just it's serial number.

    Parameters
    ----------
    device_serial_no: str
        The serial number for the device.
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    device_info: Optional[Dict[str, Any]]
        The full device information.
        None if no device found.
    """
    # Create client if none provided
    if client is None:
        client = NuminaClient()

    # Get current device by serial no
    current_device_info = client.execute(
        queries.GET_DEVICE_BY_SERIALNO.format(device_serial_no=device_serial_no)
    )

    # Device exists, return
    if len(current_device_info["devices"]["edges"]) > 0:
        return current_device_info["devices"]["edges"][0]["node"]

    # Device doesn't exist, return None
    return None


def get_device_by_name(
    device_name: str,
    client: Optional[NuminaClient] = None,
) -> Optional[Dict[str, Any]]:
    """
    Get a device's full information from just it's name.

    Parameters
    ----------
    device_name: str
        The name for the target device.
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    device_info: Optional[Dict[str, Any]]
        The full device information.
        None if no device found.
    """
    # Create client if none provided
    if client is None:
        client = NuminaClient()

    # Get current device by serial no
    current_device_info = client.execute(
        queries.GET_DEVICE_BY_NAME.format(device_name=device_name)
    )

    # Device exists, return
    if len(current_device_info["devices"]["edges"]) > 0:
        return current_device_info["devices"]["edges"][0]["node"]

    # Device doesn't exist, return None
    return None


def update_device(
    device_current_serial_no: str,
    device_new_serial_no: str,
    device_new_name: str,
    client: Optional[NuminaClient] = None,
) -> Dict[str, Any]:
    """
    Update fields on a device.

    Parameters
    ----------
    device_current_serial_no: str
        The current serial number for device to update.
    device_new_serial_no: str
        The serial number to update the device to.
        This can be the same as current if you are just changing the name.
    device_new_name: str
        The name to update the device to.
        This can be the same as current if you are just changing the serial number.
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    device_info: Dict[str, Any]
        The full updated device information.
    """
    # Create client if none provided
    if client is None:
        client = NuminaClient()

    # Get current device info
    current_device_info = get_device_by_serial_no(device_current_serial_no)

    # Update device
    return client.execute(
        mutations.UPDATE_DEVICE.format(
            device_id=current_device_info["device_id"],
            device_new_serial_no=device_new_serial_no,
            device_new_name=device_new_name,
        )
    )["updateDevice"]["device"]


def update_device_serial_no(
    current_serial_no: str,
    new_serial_no: str,
    client: Optional[NuminaClient] = None,
) -> Dict[str, Any]:
    """
    Update an existing sensors serial number.

    Parameters
    ----------
    current_serial_no: str
        The device current serial number.
    new_serial_no: str
        The serial number to set.
    client: Optional[NuminaClient]
        An optional, pre-existing NuminaClient to use for the query.
        Default: None, create new client.

    Returns
    -------
    device_details: Dict[str, Any]
        The updated device details.

    Raises
    ------
    ValueError
        No device found with the current serial number.
    ValueError
        New serial number already exists.
    """
    # Create client if none provided
    if client is None:
        client = NuminaClient()

    # Get current details
    device_details = get_device_by_serial_no(current_serial_no, client=client)

    # Handle no device found
    if device_details is None:
        raise ValueError(
            f"No current device found with serial number: {current_serial_no}"
        )

    # Check that no device is found with the target serial number
    planned_device_details = get_device_by_serial_no(new_serial_no, client=client)
    if planned_device_details is not None:
        raise ValueError(
            f"The target serial number provided already exists. "
            f"Target serial number: {new_serial_no}\n"
            f"Conflicting device: {planned_device_details}"
        )

    return client.execute(
        mutations.UPDATE_DEVICE_SERIAL_NO.format(
            device_serial_no=new_serial_no,
            device_id=device_details["device_id"],
        )
    )["updateDevice"]["device"]
