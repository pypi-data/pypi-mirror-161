#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any

import pandas as pd

###############################################################################


def filter_dataframe_to_single_result(
    df: pd.DataFrame,
    filter_col: str,
    filter_val: Any,
    no_result_fstring: str,
    many_result_fstring: str,
) -> pd.Series:
    """
    Provided a DataFrame, filter and return the found Series based off the filter value.
    If no results or too many results are found, raise a ValueError.

    Parameters
    ----------
    df: pd.DataFrame
        The dataframe to filter.
    filter_col: str
        The column to filter based off value.
    filter_val: Any
        The value to filter for.
    no_result_fstring: str
        A template string to fill with filter_val and the original dataframe.
        Will be returned with a ValueError in the case of no matching result.
    many_result_fstring: str
        A template string to fill with filter_val and the original dataframe.
        Will be returned with a ValueError in the case of too many matching results.

    Returns
    -------
    match: pd.Series
        The found Series match.

    Raises
    ------
    ValueError: either no or too many results were found from the filter operation.
    KeyError: filter_col not a valid col in the frame.
    """
    matching = df[df[filter_col] == filter_val]
    if len(matching) == 0:
        raise ValueError(no_result_fstring.format(filter_val=filter_val, df=df))
    elif len(matching) > 1:
        raise ValueError(many_result_fstring.format(filter_val=filter_val, df=df))

    return matching.iloc[0]
