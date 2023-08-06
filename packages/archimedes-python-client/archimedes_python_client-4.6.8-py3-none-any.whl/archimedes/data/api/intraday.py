from datetime import datetime
from typing import List, Union

import pandas as pd

from archimedes.data.common import get_api_base_url_v2
from archimedes.utils import get_end_date, get_start_date
from archimedes.utils.api_request import api
from archimedes.utils.split import get_queries_observation_json
from archimedes.utils.threaded_executor import execute_many
from archimedes.utils.utils import datetime_to_iso_format


def get_intraday_trades(
    price_areas: List[str] = None,
    start: Union[str, pd.Timestamp, datetime, None] = None,
    end: Union[str, pd.Timestamp, datetime, None] = None,
    *,
    access_token: str = None,
):
    """Get raw intraday trades from Archimedes Database

    This function can be used to fetch raw time series from the Archimedes Database
    without any post-processing.
    To see which series are available, use `list_ids()`.

    Example:
        >>> import archimedes
        >>> archimedes.get(
        >>>     price_areas=["NO1",],
        >>>     start="2020-06-20T04:00:00+00:00",
        >>>     end="2020-06-20T09:00:00+00:00",
        >>> )
                from_dt to_dt   series_id   version price   trade_time  buy_area    sell_area   attributes
        0	2022-03-01T00:00:00+00:00	2022-03-01T01:00:00+00:00	NP/IntradayTrades	1646193645	146.63	2022-02-28T17:02:06.934+0000	OPX	NO1	{'price': 146.63,...,  'product_code': 'PH-20220301-01'}
        1	2022-03-01T00:00:00+00:00	2022-03-01T01:00:00+00:00	NP/IntradayTrades	1646193645	146.63	2022-02-28T17:02:06.934+0000	OPX	NO1	{'price': 146.63,... , 'product_code': 'PH-20220301-01'}
        2	2022-03-01T00:00:00+00:00	2022-03-01T01:00:00+00:00	NP/IntradayTrades	1646193645	146.63	2022-02-28T17:02:06.934+0000	OPX	NO1	{'price': 146.63, ..., 'product_code': 'PH-20220301-01'}
        ...
        155	2022-03-01T23:00:00+00:00	2022-03-02T00:00:00+00:00	NP/IntradayTrades	1646193645	148.99	2022-03-01T13:05:40.934+0000	NL	NO1	{'price': 148.99,... , 'product_code': 'PH-20220301-24'}
        156	2022-03-01T23:00:00+00:00	2022-03-02T00:00:00+00:00	NP/IntradayTrades	1646193645	148.8	2022-03-01T12:57:58.777+0000	NO1	FI	{'price': 148.8,...,  'product_code': 'PH-20220301-24'}
        157	2022-03-01T23:00:00+00:00	2022-03-02T00:00:00+00:00	NP/IntradayTrades	1646193645	148.8	2022-03-01T12:58:02.115+0000	NO1	FI	{'price': 148.8, ... , 'product_code': 'PH-20220301-24'}


    Args:
        price_areas (List[str], optional): The price areas to pick, all price areas if None. Defaults to None.
        start (str, optional): The first datetime to fetch (inclusive). Returns all if None. Defaults to None.
        end (str, optional): The last datetime to fetch (exclusive). Returns all if None. Defaults to None.
        access_token (str, optional): None - access token for the API

    Returns:
        DataFrame with all the time series data

    Raises:
        HTTPError: If an HTTP error occurs when requesting the API.
        NoneAuth: If the user is unauthorized or if the authorization has expired.
    """  # pylint:disable=line-too-long

    if isinstance(price_areas, str):
        price_areas = [price_areas]

    start = datetime_to_iso_format(get_start_date(start))
    end = datetime_to_iso_format(get_end_date(end))

    queries = get_queries_observation_json(
        ["NP/IntradayTrades"],
        price_areas,
        start,
        end,
    )

    base_url = get_api_base_url_v2()

    params_array = [
        dict(
            url=f"{base_url}/observation_json/get",
            access_token=access_token,
            params=query,
        )
        for query in queries
    ]

    observation_data = execute_many(api.request, params_array)

    if len(observation_data) == 0:
        return pd.DataFrame(
            columns=[
                "from_dt",
                "to_dt",
                "series_id",
                "version",
                "price",
                "trade_time",
                "buy_area",
                "sell_area",
                "attributes",
            ]
        )
    observation_data = [
        {
            **i,
            "price": i["value"].get("price"),
            "trade_time": i["value"].get("trade_time"),
        }
        for i in observation_data
    ]
    observation_data = pd.DataFrame.from_dict(observation_data)

    # Extracting price area and series id
    observation_data[
        ["series_id1", "series_id2", "buy_area", "sell_area"]
    ] = observation_data["series_id"].str.split("/", 3, expand=True)
    observation_data["series_id"] = (
        observation_data["series_id1"] + "/" + observation_data["series_id2"]
    )
    observation_data["attributes"] = observation_data["value"]
    observation_data["attributes_str"] = observation_data["value"].astype(str)
    observation_data = observation_data.drop_duplicates(
        ["from_dt", "series_id", "attributes_str"]
    )
    observation_data = observation_data.drop(
        ["series_id1", "series_id2", "value", "version", "attributes_str"], axis=1
    )
    observation_data = observation_data.sort_values(by=["from_dt"]).reset_index(
        drop=True
    )

    return observation_data
