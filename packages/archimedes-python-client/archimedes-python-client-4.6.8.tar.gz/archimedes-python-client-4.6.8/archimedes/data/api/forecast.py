"""
A collection of functions for integrating with the Archimedes API
"""
from datetime import datetime
from typing import List, Union

import pandas as pd

from archimedes.data.common import get_api_base_url_v2
from archimedes.utils import get_end_date, get_start_date
from archimedes.utils.api_request import api
from archimedes.utils.threaded_executor import execute_many
from archimedes.utils.utils import datetime_to_iso_format


def forecast_list_ref_times(
    series_id: str,
    start: Union[str, pd.Timestamp, datetime, None] = None,
    end: Union[str, pd.Timestamp, datetime, None] = None,
    limit: int = None,
    *,
    access_token: str = None,
):
    """
    List all forecast reference times (the times that the forecast was generated)

    Args:
        series_id (str):
            The ID of the data series to find all the forecast reference times (the
            time the forecast was generated). Retrieve the complete list of series
            (both forecasts and observations) using the list_ids resource.
        start (pd.Timestamp, optional):
            The first datetime to fetch (inclusive). Returns all if not set. Should be
            specified in ISO 8601 format.
            (eg - '2021-11-29T06:00:00+00:00')
        end (pd.Timestamp, optional):
            The last datetime to fetch (exclusive). Returns all if not set. Should be
            specified in ISO 8601 format.
            (eg - '2021-11-30T06:00:00+00:00')
        limit (int, optional):
            Limit the output to a specific number of entries. No limit if not specified.
        access_token (str, optional): Access token for the API

    Example:
        >>> import archimedes
        >>> start = pd.Timestamp("2022-01-09T06:00:00+00:00")
        >>> end = pd.Timestamp("2022-01-10T06:00:00+00:00")
        >>> archimedes.forecast_list_ref_times('MET/forecast_air_temperature_2m', start, end)
                                   ref_times
        0   2022-01-10T05:00:00.000000+00:00
        1   2022-01-10T04:00:00.000000+00:00
        ...                              ...
        22  2022-01-09T07:00:00.000000+00:00
        23  2022-01-09T06:00:00.000000+00:00

    Returns:
        Dataframe with all of the forecast reference times
    """  # pylint:disable=line-too-long
    query = {
        "series_id": series_id,
        "start": datetime_to_iso_format(start),
        "end": datetime_to_iso_format(end),
        "limit": limit,
    }

    data = api.request(
        f"{get_api_base_url_v2()}/forecast/list_ref_times",
        access_token=access_token,
        params=query,
    )

    return pd.DataFrame.from_dict(data)


def forecast_diff(
    comparison_type: str,
    series_ids: List[str],
    price_areas: List[str] = None,
    ref_time1: Union[str, pd.Timestamp, datetime, None] = None,
    ref_time2: Union[str, pd.Timestamp, datetime, None] = None,
    *,
    access_token: str = None,
):
    """
    Get the difference between two different forecasts.

    Args:
        comparison_type:
            The type of comparison to do to the two forecasts:
                forecast_update - how has the forecast for a specific time range been
                    updated. The two forecast reference times must be within ~60 hours
                    of each other. Otherwise, the output will be empty (because
                    the forecasts don't overlap).
                forecast_diff - compares the forecasts of any two dates to indicate how
                    different they are.
        series_ids:
            The ID of the data series to get (eg - 'MET/forecast_air_temperature_2m' or
            'MET/forecast_wind_speed_10m'). To specify multiple data series, include
            the series_ids parameter multiple times in the url.
            Retrieve the complete list of series using the list_ids resource.
        price_areas:
            The name of the price area(eg - 'NO2', 'NO5', or 'DE1-NO1'). To specify
            multiple price areas, include the price_areas parameter multiple times in
            the url.
            Retrieve the complete list of price areas available for a specified series
            ID using list_series_price_areas resource.
        ref_time1:
            Specify one of the two timestamps for when a forecast was created. Should
            be specified in ISO 8601 format (eg - '2021-11-29T06:00:00+00:00').
        ref_time2:
            Specify another of the two timestamps for when a forecast was
            created. Should be specified in ISO 8601 format
            (eg - '2021-11-29T06:00:00+00:00').
        access_token (str, optional):
            Access token for the API

    Returns:
        Dataframe with the diff of the two forecasts
    """
    assert comparison_type in ["forecast_update", "forecast_diff",], (
        f"Unknown comparison_type '{comparison_type}' "
        f"(should be either 'forecast_update' or 'forecast_diff')"
    )
    query = {
        "forecast_comparison_type": comparison_type,
        "series_ids": series_ids,
        "price_areas": price_areas,
        "ref_time1": datetime_to_iso_format(ref_time1),
        "ref_time2": datetime_to_iso_format(ref_time2),
    }

    data = api.request(
        f"{get_api_base_url_v2()}/forecast/diff",
        access_token=access_token,
        params=query,
    )

    return pd.DataFrame.from_dict(data)


def forecast_get(
    series_ids: List[str],
    price_areas: List[str] = None,
    start: Union[str, pd.Timestamp, datetime, None] = None,
    end: Union[str, pd.Timestamp, datetime, None] = None,
    *,
    access_token: str = None,
):
    """Get any number of forecast time series.

    This function can be used to fetch time series from the Archimedes Database.
    To see which series are available, use `list_ids()`.

    Example:
        >>> import archimedes
        >>> archimedes.get(
        >>>     series_ids=["MET/forecast_wind_speed_10m"],
        >>>     price_areas=["NO1", "NO2"],
        >>>     start="2022-04-20T06:00:00+00:00",
        >>>     end="2022-04-20T12:00:00+00:00",
        >>> )
        series_id                 MET/forecast_wind_speed_10m
        price_area                          NO1   NO2
        from_dt
        2020-06-20T04:00:00+00:00          1.30  1.30
        2020-06-20T05:00:00+00:00          1.35  1.35
        ...                                 ...   ...
        2020-06-28T03:00:00+00:00          0.53  0.53
        2020-06-28T04:00:00+00:00          0.55  0.55

    Args:
        series_ids (List[str]): The series ids to get.
        price_areas (List[str], optional): The price areas to pick, all price areas if
                                           None. Defaults to None.
        start (str, optional): The first datetime to fetch (inclusive). Returns all if
                               None. Defaults to None.
        end (str, optional): The last datetime to fetch (exclusive). Returns all if
                             None. Defaults to None.
        access_token (str, optional): None - access token for the API

    Returns:
        DataFrame with all the time series data

    Raises:
        HTTPError: If an HTTP error occurs when requesting the API.
        NoneAuth: If the user is unauthorized or if the authorization has expired.
    """

    if isinstance(series_ids, str):
        series_ids = [series_ids]

    if isinstance(price_areas, str):
        price_areas = [price_areas]

    start = datetime_to_iso_format(get_start_date(start))
    end = datetime_to_iso_format(get_end_date(end))

    queries = [
        {
            "start": start,
            "end": end,
            "series_ids": series_id,
            "price_areas": price_areas,
        }
        for series_id in series_ids
    ]

    base_url = get_api_base_url_v2()
    params_array = [
        dict(url=f"{base_url}/forecast/get", access_token=access_token, params=query)
        for query in queries
    ]
    data = execute_many(api.request, params_array)

    if len(data) == 0:
        df = pd.DataFrame(
            columns=["series_id", "from_dt", "ref_dt", "value", "price_area"]
        )
    else:
        df = pd.DataFrame.from_dict(data)
        df = df.sort_values(by=["from_dt", "ref_dt"])

    df["from_dt"] = pd.to_datetime(df["from_dt"])
    df["ref_dt"] = pd.to_datetime(df["ref_dt"])
    df = df.pivot_table(
        values="value",
        columns=["series_id", "price_area"],
        index=["from_dt", "ref_dt"],
        aggfunc="last",
    )
    return df


def forecast_get_by_ref_time_interval(  # pylint:disable=too-many-arguments
    series_id: str,
    price_area: str,
    start: Union[str, pd.Timestamp, datetime, None] = None,
    end: Union[str, pd.Timestamp, datetime, None] = None,
    forecast_interval: int = 24,
    day_ahead_hour: int = None,
    *,
    access_token: str = None,
):
    """
    Get a single forecast value for every hour. The value should be from the forecast
    that was generated at least forecast_interval hours prior.

    Args:
        series_id:
            The ID of the data series to get (eg - 'MET/forecast_air_temperature_2m' or
            'MET/forecast_wind_speed_10m'). Retrieve the complete list of series using
            the list_ids resource.
        price_area:
            The name of the price area(eg - 'NO2', 'SE3'). Retrieve the complete list
            of price areas available for a specified series ID using
            list_series_price_areas resource.
        start:
            The first datetime to fetch (inclusive). Returns all if not set. Should be
            specified in ISO 8601 format (eg - '2021-11-29T06:00:00+00:00')
        end:
            The last datetime to fetch (exclusive). Returns all if not set. Should be
            specified in ISO 8601 format (eg - '2021-11-30T06:00:00+00:00')
        forecast_interval:
            The number of hours earlier that the forecast must have been generated. In
            some cases, it could be older (if no forecast was generated at exactly that
            hour). NOTE - this is ignored if day_ahead_hour is set.
        day_ahead_hour:
            Used for day-ahead market. Indicates the hour of the day when the market
            closes (CET - Central European Time). Will return the forecast generated
            before this time on the previous day
            ('forecast_interval' will be set to 24). For example, if set to '12'
            (noon CET), the values shown for every hour of a specific day will be
            fetched from the most recent forecast generated before noon (most likely
            11am) on the previous day.
        access_token (str, optional): Access token for the API

    Returns:
        Dataframe with the forecasted values
    """
    query = {
        "series_id": series_id,
        "price_area": price_area,
        "start": datetime_to_iso_format(start),
        "end": datetime_to_iso_format(end),
        "forecast_interval": forecast_interval,
        "day_ahead_hour": day_ahead_hour,
    }

    data = api.request(
        f"{get_api_base_url_v2()}/forecast/get_by_ref_time_interval",
        access_token=access_token,
        params=query,
    )

    return pd.DataFrame.from_dict(data)
