#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Tuple

import numpy as np
import pandas as pd

###############################################################################


def clean_pivot_and_split_zone_count_metrics(
    zone_metrics: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Pivots and splits up the returned data from a zone count metrics query
    (db.get_zone_count_metrics) into cleaner and more relevant subsections.

    Parameters
    ----------
    zone_metrics: pd.DataFrame
        The zone count metrics data for a single zone.
        See: db.get_zone_count_metrics

    Returns
    -------
    zone_metrics: pd.DataFrame
        Cleaned zone metrics data with some additions such as splitting the time into
        more useful parts as a new DataFrame.
    metrics_sum: pd.DataFrame
        The pivoted metrics where each row represents a different time and columns are
        available for each object class detailing how many of that object was detected
        during the row's timeframe.
    metrics_sum_weekday: pd.DataFrame
        The same format as the transposed metrics but for only the rows that fall on
        weekdays.
    metrics_sum_weekend: pd.DataFrame
        The same format as the transposed metrics but for only the rows that fall on
        weekends.
    """
    # Work off of a copy
    zone_metrics = zone_metrics.copy()

    # Create columns from object classes
    metrics_p = zone_metrics.pivot(index="time", columns="objClass", values="result")

    # Create sum values for each object class
    metrics_p_sum = metrics_p.groupby("time").sum().reset_index()

    # Return to normal dataframe
    metrics_sum = metrics_p_sum.reset_index(drop=True).rename_axis(None, axis=1)

    # Clean up time by removing the trailing timezone delta
    metrics_sum["local_datetime"] = metrics_sum.time.apply(lambda x: x[:-6])
    metrics_sum = metrics_sum.drop(["time"], axis=1)
    metrics_sum.local_datetime = pd.to_datetime(metrics_sum.local_datetime)

    # Create date, day of the week, just time columns
    metrics_sum["local_date_str"] = metrics_sum.local_datetime.dt.date.astype(str)
    metrics_sum["local_date"] = pd.to_datetime(metrics_sum.local_date_str)
    metrics_sum["local_day_name"] = metrics_sum.local_datetime.dt.day_name()
    metrics_sum["local_time"] = metrics_sum.local_datetime.dt.time

    metrics_sum["weekday"] = metrics_sum.local_day_name.isin(
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    )
    metrics_sum["part_of_week"] = np.where(metrics_sum.weekday, "Weekday", "Weekend")

    # Use todays date as the basis for storing the time as a full datetime
    # useful for plotting
    today = datetime.now().date()
    metrics_sum["local_time_as_dt"] = metrics_sum.local_time.apply(
        lambda x: datetime.combine(today, x)
    )

    # Clean up the original dataframe with the same columns for return
    zone_metrics["local_datetime"] = zone_metrics.time.apply(lambda x: x[:-6])
    zone_metrics = zone_metrics.drop(["time"], axis=1)
    zone_metrics.local_datetime = pd.to_datetime(zone_metrics.local_datetime)

    # Create date, day of week, and just time columns on original dataframe
    zone_metrics["local_date_str"] = zone_metrics.local_datetime.dt.date.astype(str)
    zone_metrics["local_date"] = pd.to_datetime(zone_metrics.local_date_str)
    zone_metrics["local_day_name"] = zone_metrics.local_datetime.dt.day_name()
    zone_metrics["local_time"] = zone_metrics.local_datetime.dt.time

    zone_metrics["weekday"] = zone_metrics.local_day_name.isin(
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    )
    zone_metrics["part_of_week"] = np.where(zone_metrics.weekday, "Weekday", "Weekend")

    # Use todays date as the basis for storing the time as a full datetime
    zone_metrics["local_time_as_dt"] = zone_metrics.local_time.apply(
        lambda x: datetime.combine(today, x)
    )

    # Change column names a bit on original data
    zone_metrics = zone_metrics.rename(
        {"objClass": "obj_class", "result": "count"},
        axis=1,
    )

    # Remove extra columns
    if "zone_id" in zone_metrics.columns:
        zone_metrics = zone_metrics.drop("zone_id", axis=1)
    if "metric" in zone_metrics.columns:
        zone_metrics = zone_metrics.drop("metric", axis=1)

    # Object classes in summed zone metrics
    # By describing the dataframe we get rid of any extra "local time" and such cols
    object_classes = metrics_sum.describe().columns.values

    # Create day sum for each obj class
    for obj_class in object_classes:
        metrics_sum[f"day_sum_{obj_class}"] = metrics_sum.groupby("local_date")[
            obj_class
        ].transform("sum")

    # Create weekday and weekend splits
    metrics_sum_weekday = metrics_sum[metrics_sum.weekday]
    metrics_sum_weekend = metrics_sum[~metrics_sum.weekday]

    return zone_metrics, metrics_sum, metrics_sum_weekday, metrics_sum_weekend


def get_zone_activity(summed_zone_metrics: pd.DataFrame) -> pd.DataFrame:
    """
    Provides a dataframe similar to pandas describe but has object class, sum, and
    percent of total columns where each row is a different object class.

    Parameters
    ----------
    summed_zone_metrics: pd.DataFrame
        The summed zone metrics to get activity for.
        See: metrics.pivot_and_split_zone_count_metrics

    Returns
    -------
    zone_activity: pd.DataFrame
        The zone metrics in descriptive form for sum and percent of total.
    """
    # Object classes in summed zone metrics
    # By describing the dataframe we get rid of any extra "local time" and such cols
    object_classes = summed_zone_metrics.describe().columns.values

    # Create activity dict for storage
    activity = {}
    total_object_count = 0

    # Creates a list of percentage amounts and types for all objects in obj_types
    for obj_class in object_classes:
        obj_count = summed_zone_metrics[obj_class].sum()
        activity[obj_class] = obj_count
        total_object_count += obj_count

    # Format into dataframe
    formatted_activity = pd.DataFrame(
        [
            {
                "Object Class": obj_class,
                "Sum": obj_count,
                "Percent of Total": obj_count / total_object_count,
            }
            for obj_class, obj_count in activity.items()
        ]
    )

    return pd.DataFrame(formatted_activity)
