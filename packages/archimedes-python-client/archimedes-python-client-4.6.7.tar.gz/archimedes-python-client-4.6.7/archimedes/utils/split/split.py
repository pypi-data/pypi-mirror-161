"""
Query splitting strategy for best performance
"""
import re
from datetime import datetime
from typing import Dict, List, Union

import numpy as np
import pandas as pd
from iteration_utilities import unique_everseen

from archimedes.utils.utils import datetime_to_iso_format, get_end_date, get_start_date

from .config import (
    DATE_RANGE,
    DEFAULT_NUMBER_OF_SUB_IDS,
    NUMBER_OF_DATA_POINTS_PER_HOUR,
    PERMUTATION_RESULTS,
    SPLIT_REQUEST_AT_SIZE_BYTES,
    UNIT_DATA_SIZE_BY_SERIES,
)


def get_queries(  # pylint:disable=too-many-branches,too-many-locals
    series_ids: List[str],
    price_areas: Union[List[str], None],
    start: Union[str, pd.Timestamp, datetime, None],
    end: Union[str, pd.Timestamp, datetime, None],
    is_json_query: bool,
) -> List[Dict]:
    """
    Get split queries
    Args:
        series_ids (List[str]):
        The series ids to get.

        price_areas (Union[List[str], None]):
        The price areas to pick.

        start (Union[str, pd.Timestamp, datetime, None])):
        The first datetime to request.

        end (Union[str, pd.Timestamp, datetime, None])):
        The last datetime to request.

        is_json_query (bool):
        True if the query is to be made for observations_json or if it is to be made
        for data/get.

    Returns:
        List of split up queries.
    """
    if series_ids is None or len(series_ids) == 0:
        return []

    start, end = get_start_date(start), get_end_date(end)

    series_metadata = get_series_metadata(series_ids, price_areas, start, end)
    sum_approx_response_size_in_bytes = (
        -1 if series_metadata.empty else series_metadata["sum"]["approx_size_in_bytes"]
    )

    if sum_approx_response_size_in_bytes < SPLIT_REQUEST_AT_SIZE_BYTES:
        if not is_json_query:
            return [
                {
                    "start": datetime_to_iso_format(start),
                    "end": datetime_to_iso_format(end),
                    "series_ids": sorted(series_ids),
                    "price_areas": price_areas,
                }
            ]

        queries = [
            {
                "start": datetime_to_iso_format(start),
                "end": datetime_to_iso_format(end),
                "series_id": series_id,
                "price_areas": price_areas,
            }
            for series_id in series_ids
        ]
        return list(unique_everseen(queries))

    large_series_ids = []
    if not series_metadata.empty:
        for series_id in series_ids:
            if (
                series_metadata[series_id]["approx_size_in_bytes"]
                >= SPLIT_REQUEST_AT_SIZE_BYTES
            ):
                large_series_ids.append(series_id)

    large_queries = []
    for large_series_id in large_series_ids:
        duration = (end - start).total_seconds() / 2
        for offset in range(2):
            actual_start = start + pd.Timedelta(seconds=offset * duration)
            possible_end = actual_start + pd.Timedelta(seconds=duration)
            actual_end = min(end, possible_end)
            large_queries.extend(
                get_queries(
                    [large_series_id],
                    price_areas,
                    actual_start,
                    actual_end,
                    is_json_query,
                )
            )

    remaining_series_ids = list(set(series_ids) - set(large_series_ids))

    if is_json_query:
        remaining_queries = [
            {
                "start": datetime_to_iso_format(start),
                "end": datetime_to_iso_format(end),
                "series_id": series_id,
                "price_areas": price_areas,
            }
            for series_id in remaining_series_ids
        ]
    else:
        if len(remaining_series_ids) == 0:
            remaining_queries = []
        elif len(remaining_series_ids) == 1:
            remaining_queries = [
                {
                    "start": datetime_to_iso_format(start),
                    "end": datetime_to_iso_format(end),
                    "series_ids": sorted(remaining_series_ids),
                    "price_areas": price_areas,
                }
            ]
        else:
            if large_queries:
                # In this case, some large queries were contributing to the split
                # requirement but maybe the remaining queries don't need to be split
                # at all. Also, since remaining_queries is a subset of series_ids
                # without the large queries, it should never lead to infinite recursion.
                remaining_queries = get_queries(
                    remaining_series_ids, price_areas, start, end, is_json_query
                )
            else:
                remaining_queries = []
                for half_series_ids in np.array_split(np.sort(remaining_series_ids), 2):
                    remaining_queries.extend(
                        get_queries(
                            sorted(list(half_series_ids)),
                            price_areas,
                            start,
                            end,
                            is_json_query,
                        )
                    )

    return list(unique_everseen(large_queries + remaining_queries))


def get_queries_observation(
    series_ids: List[str],
    price_areas: List[str],
    start: Union[str, pd.Timestamp, datetime, None],
    end: Union[str, pd.Timestamp, datetime, None],
) -> List[Dict]:
    """
    Get split queries
    Args:
        series_ids (List[str]): The series ids to get.
        price_areas (Union[List[str], None]): The price areas to pick.
        start (Union[str, pd.Timestamp, None])): The first datetime to request.
        end (Union[str, pd.Timestamp, NOne])): The last datetime to request.

    Returns:
        List[Dict]: List of split up queries.
    """
    return get_queries(series_ids, price_areas, start, end, False)


def get_queries_observation_json(
    series_ids: List[str],
    price_areas: List[str],
    start: Union[str, pd.Timestamp, datetime, None],
    end: Union[str, pd.Timestamp, datetime, None],
) -> List[Dict]:
    """
    Get split queries
    Args:
        series_ids (List[str]): The series ids to get.
        price_areas (Union[List[str], None]): The price areas to pick.
        start (Union[str, pd.Timestamp, None])): The first datetime to request.
        end (Union[str, pd.Timestamp, NOne])): The last datetime to request.

    Returns:
        List[Dict]: List of split up queries.
    """
    return get_queries(series_ids, price_areas, start, end, True)


def get_series_metadata(
    series_ids: List[str],
    price_areas: List[str],
    start: Union[str, pd.Timestamp, datetime, None],
    end: Union[str, pd.Timestamp, datetime, None],
):
    """
    Get series metadata
    Args:
        series_ids (List[str]):
        The series ids to get.

        price_areas (Union[List[str], None]):
        The price areas to pick.

        start (Union[str, pd.Timestamp, datetime, None])):
        The first datetime to request.

        end (Union[str, pd.Timestamp, datetime, None])):
        The last datetime to request.

    Returns:
        pd.DataFrame: A dataframe with information about the requested
                      range for the series.
    """
    series_metadata = {}

    for series_id in series_ids:
        actual_start, actual_end, hours_of_data = _get_hours_of_data(
            series_id, start, end
        )
        number_of_rows = _get_number_of_rows(series_id, hours_of_data)
        number_of_columns = _get_number_of_columns(series_id, price_areas)
        approx_size_in_bytes = _get_approx_size_in_bytes(
            series_id,
            number_of_columns,
            number_of_rows,
        )
        series_metadata[series_id] = {
            "actual_start": actual_start,
            "actual_end": actual_end,
            "hours_of_data": hours_of_data,
            "number_of_columns": number_of_columns,
            "number_of_rows": number_of_rows,
            "approx_size_in_bytes": approx_size_in_bytes,
        }

    df = pd.DataFrame.from_dict(series_metadata)
    df["sum"] = df.loc["approx_size_in_bytes"].sum()
    return df


def _get_hours_of_data(series_id, start, end):
    for match_string, (series_start_date, series_end_date) in DATE_RANGE.items():
        if re.match(match_string, series_id):
            hours_start = max(start, series_start_date)
            hours_end = min(end, series_end_date)
            hours_of_data = max((hours_end - hours_start).total_seconds() / 3600, 0)
            return hours_start, hours_end, hours_of_data
    return None, None, None


def _get_number_of_columns(series_id, price_areas):
    """
    This will return a wrong value if some price_areas do not exist for a series
    which needs_permutation.
    """
    r = _get_num_columns_needs_permutation(series_id)  # pylint:disable=invalid-name

    if price_areas and r is False:
        return len(price_areas)

    for match_string, num_columns in DEFAULT_NUMBER_OF_SUB_IDS.items():
        if re.match(match_string, series_id):
            if r is False:
                return num_columns
            perms = np.math.factorial(num_columns) / np.math.factorial(num_columns - r)
            if not price_areas:
                return perms
            perms_of_rest = np.math.factorial(
                num_columns - len(price_areas)
            ) / np.math.factorial(num_columns - len(price_areas) - r)
            net_perms = perms - perms_of_rest
            if net_perms >= 0:
                return net_perms
            return perms

    return None


def _get_num_columns_needs_permutation(series_id):
    for match_string, num_at_a_time in PERMUTATION_RESULTS.items():
        if re.match(match_string, series_id):
            return num_at_a_time

    return False


def _get_number_of_rows(series_id, hours_of_data):
    for match_string, num_rows_per_hour in NUMBER_OF_DATA_POINTS_PER_HOUR.items():
        if re.match(match_string, series_id):
            return num_rows_per_hour * hours_of_data

    return None


def _get_approx_size_in_bytes(series_id, number_of_columns, number_of_rows):
    for match_string, unit_size_in_bytes in UNIT_DATA_SIZE_BY_SERIES.items():
        if re.match(match_string, series_id):
            return number_of_columns * number_of_rows * unit_size_in_bytes

    return None
