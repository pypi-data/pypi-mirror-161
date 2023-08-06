from datetime import datetime
from typing import List, Union

import pandas as pd

from archimedes.data.common import get_api_base_url_v2
from archimedes.utils import get_end_date, get_start_date
from archimedes.utils.api_request import api
from archimedes.utils.split import get_queries_observation, get_queries_observation_json
from archimedes.utils.threaded_executor import execute_many
from archimedes.utils.utils import datetime_to_iso_format


def get(  # pylint:disable=too-many-locals
    series_ids: List[str],
    price_areas: List[str] = None,
    start: Union[str, pd.Timestamp, datetime, None] = None,
    end: Union[str, pd.Timestamp, datetime, None] = None,
    *,
    access_token: str = None,
):
    """Get any number of time series.

    This function can be used to fetch time series from the Archimedes Database.
    To see which series are available, use `list_ids()`.

    Example:
        >>> import archimedes
        >>> archimedes.get(
        >>>     series_ids=["NP/AreaPrices"],
        >>>     price_areas=["NO1", "NO2"],
        >>>     start="2020-06-20T04:00:00+00:00",
        >>>     end="2020-06-28T04:00:00+00:00",
        >>> )
        series_id                 NP/AreaPrices
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

    if not series_ids:
        return pd.DataFrame()

    if isinstance(series_ids, str):
        series_ids = [series_ids]

    if isinstance(price_areas, str):
        price_areas = [price_areas]

    start = datetime_to_iso_format(get_start_date(start))
    end = datetime_to_iso_format(get_end_date(end))

    observation_series_ids, observation_json_series_ids = _split_series_ids(
        series_ids, access_token
    )

    queries_by_type = {
        "observations": get_queries_observation(
            observation_series_ids, price_areas, start, end
        ),
        "observations_json": get_queries_observation_json(
            observation_json_series_ids, price_areas, start, end
        ),
    }

    def _make_observation_or_observation_json_request(request_type, params):
        request_url_path = (
            "data" if request_type == "observations" else "observation_json"
        )
        query_result = api.request(
            f"{get_api_base_url_v2()}/{request_url_path}/get",
            params=params,
            access_token=access_token,
        )
        return request_type, query_result

    def _merge_function(result, aggr):
        if aggr is None:
            aggr = {}
        observation_type, value = result
        if observation_type not in aggr.keys():
            aggr[observation_type] = []
        aggr[observation_type].extend(value)
        return aggr

    params_array = []
    for query_type, queries in queries_by_type.items():
        for query in queries:
            params_array.append(dict(request_type=query_type, params=query))

    api_results = execute_many(
        _make_observation_or_observation_json_request, params_array, _merge_function
    )

    observations = _process_observations(api_results.get("observations", []))
    observations_json = _process_observations_json(
        api_results.get("observations_json", [])
    )

    if observations_json.empty and observations.empty:
        return pd.DataFrame()

    if observations.empty:
        df = observations_json
    elif observations_json.empty:
        df = observations
    else:
        df = pd.merge(
            observations,
            observations_json,
            left_index=True,
            right_index=True,
            how="outer",
        )

    df.index = pd.to_datetime(df.index)

    return df


def get_latest(
    series_ids: List[str],
    price_areas: List[str] = None,
    *,
    access_token: str = None,
):
    """Get the most recent data for any number of time series.

    This function is similar to `get()`, but only fetches data from the past 48 hours,
    potentially including future hours as well (as in the case of Spot price data).

    @TODO: Add an argument `hours` that allows the 'lookback' period to be extended
    to an arbitrary number of hours.

    Example:
        >>> import archimedes
        >>> # Calling this function at 2020-03-15T10:15:00
        >>> archimedes.get_latest(
        >>>     series_ids=["NP/AreaPrices", "NP/ConsumptionImbalancePrices"],
        >>>     price_areas=["NO1"],
        >>> )
        series_id                 NP/AreaPrices  NP/ConsumptionImbalancePrices
        price_area                          NO1                            NO1
        from_dt
        2020-03-14T04:11:00+00:00          1.30                           1.30
        2020-03-14T05:12:00+00:00          1.35                           1.35
        ...                                 ...                            ...
        2020-03-15T22:00:00+00:00          0.53                            NaN
        2020-03-15T23:00:00+00:00          0.55                            NaN

    Args:
        series_ids (List[str]): The series ids to get.
        price_areas (List[str], optional): The price areas to pick, all price areas if
                                           None. Defaults to None.
        access_token (str, optional): None - access token for the API

    Returns:
        DataFrame with the latest time series data

    Raises:
        HTTPError: If an HTTP error occurs when requesting the API.
        NoneAuth: If the user is unauthorized or if the authorization has expired.
    """
    now_dt = pd.Timestamp.now(tz="utc")
    start_dt = now_dt - pd.Timedelta(days=2)
    # +14 days should be enough in all cases now:
    end_dt = now_dt + pd.Timedelta(days=14)

    df = get(
        series_ids=series_ids,
        price_areas=price_areas,
        start=datetime_to_iso_format(start_dt),
        end=datetime_to_iso_format(end_dt),
        access_token=access_token,
    )

    return df


def _split_series_ids(series_ids, access_token=None):
    base_url = get_api_base_url_v2()
    all_series_ids_observations = api.request(
        f"{base_url}/data/list_ids", access_token=access_token
    )
    all_series_ids_observations_json = api.request(
        f"{base_url}/observation_json/list_ids",
        access_token=access_token,
    )
    series_ids_observations = [
        series_id
        for series_id in series_ids
        if series_id in all_series_ids_observations["series_id"]
    ]
    series_ids_observations_json = [
        series_id
        for series_id in series_ids
        if series_id in all_series_ids_observations_json["series_id"]
    ]

    # Add series ids that exist in none of the list_ids to both
    series_ids_none = [
        series_id
        for series_id in series_ids
        if series_id not in series_ids_observations
        and series_id not in series_ids_observations_json
    ]
    series_ids_observations.extend(series_ids_none)
    series_ids_observations_json.extend(series_ids_none)

    return series_ids_observations, series_ids_observations_json


def _process_observations(observations):
    observations = pd.DataFrame(observations)
    if not observations.empty:
        observations = observations.sort_values(by=["from_dt", "version"]).pivot_table(
            values="value",
            columns=["series_id", "price_area"],
            index="from_dt",
            aggfunc="last",
        )
    return observations


def _process_observations_json(observations):
    observations_json = pd.DataFrame(observations)
    if not observations_json.empty:
        observations_json[
            ["series_id1", "series_id2", "price_area"]
        ] = observations_json["series_id"].str.split("/", 2, expand=True)
        observations_json["series_id"] = (
            observations_json["series_id1"] + "/" + observations_json["series_id2"]
        )
        observations_json = observations_json.drop(["series_id1", "series_id2"], axis=1)
        is_intraday_trades = observations_json["series_id"] == "NP/IntradayTrades"

        def agg_func(items):
            return list(items)

        observation_data_intraday = observations_json[is_intraday_trades]
        if len(observation_data_intraday):
            observation_data_intraday = observation_data_intraday.sort_values(
                by=["from_dt"]
            )
            observation_data_intraday = observation_data_intraday.pivot_table(
                values="value",
                columns=["series_id", "price_area"],
                index="from_dt",
                aggfunc=agg_func,
            )

        observations_json = observations_json[~is_intraday_trades]
        if len(observations_json):
            observations_json = observations_json.sort_values(
                by=["from_dt", "version"]
            ).pivot_table(
                values="value",
                columns=["series_id", "price_area"],
                index="from_dt",
                aggfunc="last",
            )

        if observation_data_intraday.empty and observations_json.empty:
            observations_json = pd.DataFrame()
        elif observation_data_intraday.empty:
            pass
        elif observations_json.empty:
            observations_json = observation_data_intraday
        else:
            observations_json = observations_json.merge(
                observation_data_intraday,
                left_index=True,
                right_index=True,
                how="outer",
            )
    return observations_json
