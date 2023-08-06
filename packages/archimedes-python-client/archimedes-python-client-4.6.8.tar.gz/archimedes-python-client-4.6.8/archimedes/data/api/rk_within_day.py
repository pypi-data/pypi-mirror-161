from datetime import datetime
from typing import Union

import pandas as pd

from archimedes.data.common import get_api_base_url_v2
from archimedes.utils.api_request import api
from archimedes.utils.utils import datetime_to_iso_format


def rk_within_day_directions(
    start: Union[str, pd.Timestamp, datetime],
    end: Union[str, pd.Timestamp, datetime],
    price_area: str,
    ref_dt: Union[str, pd.Timestamp, datetime, None] = None,
    *,
    access_token: str = None,
):
    """
    Method to get directions for rk within day
    Parameters:
        start: Start timestamp
        end: end timestamp
        price_area: Price area
        ref_dt: Reference timestamp
        access_token: Access token
    """
    start = datetime_to_iso_format(start)
    end = datetime_to_iso_format(end)
    ref_dt = datetime_to_iso_format(ref_dt)
    query = {
        "start": start,
        "end": end,
        "price_area": price_area,
    }
    if ref_dt is not None:
        query["ref_dt"] = ref_dt
    data = api.request(
        f"{get_api_base_url_v2()}/rk_within_day/directions",
        access_token=access_token,
        params=query,
    )
    return pd.DataFrame.from_dict(data)


def rk_within_day_distributions(
    start: Union[str, pd.Timestamp, datetime],
    end: Union[str, pd.Timestamp, datetime],
    price_area: str,
    ref_dt: Union[str, pd.Timestamp, datetime, None] = None,
    *,
    access_token: str = None,
):
    """
    Method to get distributions for rk within day
    Parameters:
        start: Start timestamp
        end: end timestamp
        price_area: Price area
        ref_dt: Reference timestamp
        access_token: Access token
    """
    start = datetime_to_iso_format(start)
    end = datetime_to_iso_format(end)
    ref_dt = datetime_to_iso_format(ref_dt)
    query = {
        "start": start,
        "end": end,
        "price_area": price_area,
    }
    if ref_dt is not None:
        query["ref_dt"] = ref_dt
    data = api.request(
        f"{get_api_base_url_v2()}/rk_within_day/distributions",
        access_token=access_token,
        params=query,
    )
    return pd.DataFrame.from_dict(data)


def rk_within_day_large_up_fps(
    start: Union[str, pd.Timestamp, datetime],
    end: Union[str, pd.Timestamp, datetime],
    price_area: str,
    ref_dt: Union[str, pd.Timestamp, datetime, None] = None,
    conditional: bool = False,
    *,
    access_token: str = None,
):
    """
    Method to get large up for rk within day
    Parameters:
        start: Start timestamp
        end: end timestamp
        price_area: Price area
        ref_dt: Reference timestamp
        conditional: If set to False, ignores the direction of RK
        access_token: Access token
    """
    start = datetime_to_iso_format(start)
    end = datetime_to_iso_format(end)
    ref_dt = datetime_to_iso_format(ref_dt)
    query = {
        "start": start,
        "end": end,
        "price_area": price_area,
        "conditional": conditional,
    }
    if ref_dt is not None:
        query["ref_dt"] = ref_dt
    data = api.request(
        f"{get_api_base_url_v2()}/rk_within_day/large_up_fps",
        access_token=access_token,
        params=query,
    )
    return pd.DataFrame.from_dict(data)


def rk_within_day_large_down_fps(
    start: Union[str, pd.Timestamp, datetime],
    end: Union[str, pd.Timestamp, datetime],
    price_area: str,
    ref_dt: Union[str, pd.Timestamp, datetime, None] = None,
    conditional: bool = False,
    *,
    access_token: str = None,
):
    """
    Method to get large down for rk within day
    Parameters:
        start: Start timestamp
        end: end timestamp
        price_area: Price area
        ref_dt: Reference timestamp
        conditional: If set to False, ignores the direction of RK
        access_token: Access token
    """
    start = datetime_to_iso_format(start)
    end = datetime_to_iso_format(end)
    ref_dt = datetime_to_iso_format(ref_dt)
    query = {
        "start": start,
        "end": end,
        "price_area": price_area,
        "conditional": conditional,
    }
    if ref_dt is not None:
        query["ref_dt"] = ref_dt
    data = api.request(
        f"{get_api_base_url_v2()}/rk_within_day/large_down_fps",
        access_token=access_token,
        params=query,
    )
    return pd.DataFrame.from_dict(data)


def rk_comparison_by_price(
    start: Union[str, pd.Timestamp, datetime],
    end: Union[str, pd.Timestamp, datetime],
    price_area: str,
    ref_price: int,
    ref_dt: Union[str, pd.Timestamp, datetime, None] = None,
    *,
    access_token: str = None,
):
    """
    Method to get probability for rk within day in comparison to provided price
    Parameters:
        start: Start timestamp
        end: End timestamp
        price_area: Price area
        ref_price: Reference price to compare against
        ref_dt:
            Reference time for predictions.
            Defaults to None.
            If None, the latest available is used.
        access_token: Access token
    """
    start = datetime_to_iso_format(start)
    end = datetime_to_iso_format(end)
    ref_dt = datetime_to_iso_format(ref_dt)
    query = {
        "start": start,
        "end": end,
        "price_area": price_area,
        "ref_price": ref_price,
        "ref_dt": ref_dt,
    }
    data = api.request(
        f"{get_api_base_url_v2()}/rk_within_day/price_comparison/by_price",
        access_token=access_token,
        params=query,
    )
    return pd.DataFrame.from_dict(data)


def rk_comparison_by_probability(
    start: Union[str, pd.Timestamp, datetime],
    end: Union[str, pd.Timestamp, datetime],
    price_area: str,
    ref_probability: int,
    ref_dt: Union[str, pd.Timestamp, datetime, None] = None,
    *,
    access_token: str = None,
):
    """
    Method to get probability for rk within day in comparison to provided price
    Parameters:
        start: Start timestamp
        end: End timestamp
        price_area: Price area
        ref_probability: Reference probability to compare against
        ref_dt:
            Reference time for predictions.
            Defaults to None.
            If None, the latest available is used.
        access_token: Access token
    """
    start = datetime_to_iso_format(start)
    end = datetime_to_iso_format(end)
    ref_dt = datetime_to_iso_format(ref_dt)
    query = {
        "start": start,
        "end": end,
        "price_area": price_area,
        "ref_probability": ref_probability,
        "ref_dt": ref_dt,
    }
    data = api.request(
        f"{get_api_base_url_v2()}/rk_within_day/price_comparison/by_probability",
        access_token=access_token,
        params=query,
    )
    return pd.DataFrame.from_dict(data)
