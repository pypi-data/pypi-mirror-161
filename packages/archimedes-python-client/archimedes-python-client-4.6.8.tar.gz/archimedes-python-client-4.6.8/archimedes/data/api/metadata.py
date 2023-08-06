import pandas as pd

from archimedes.data.common import get_api_base_url_v2
from archimedes.utils.api_request import api


def list_series_price_areas(series_id: str, *, access_token: str = None):
    """
    Retrieve all the price_areas which are available for the specified data series

    Example:
        >>> import archimedes
        >>> archimedes.list_series_price_areas('NP/AreaPrices')
           price_areas
        0          DK1
        1          DK2
        ...        ...
        10         SE3
        11         SE4

    Returns:
        Dataframe with all available price areas for the specified series_id
    """
    query = {
        "series_id": series_id,
    }
    base_url = get_api_base_url_v2()
    data = api.request(
        f"{base_url}/data/list_series_price_areas",
        access_token=access_token,
        params=query,
    )
    data = pd.DataFrame.from_dict(data)

    observation_data = api.request(
        f"{base_url}/observation_json/list_series_price_areas",
        access_token=access_token,
        params=query,
    )
    observation_data = pd.DataFrame.from_dict(observation_data)

    price_area_df = pd.concat([data, observation_data]).drop_duplicates()
    price_area_df = price_area_df.sort_values("price_areas").reset_index(drop=True)
    return price_area_df


def list_ids(sort: bool = False, *, access_token: str = None):
    """List all the series ids available.

    Example:
        >>> import archimedes
        >>> archimedes.list_ids()
                                    series_id
        0   NP/NegativeProductionImbalancePrices
        1                    NP/ProductionTotals
        ..                                   ...
        38                 NP/OrdinaryDownVolume
        39                    NP/SpecialUpVolume

    Args:
        sort (bool): False - return all series in one dataframe column, True - order
                             dataframe by data-origin
        access_token (str, optional): None - access token for the API

    Returns:
        DataFrame with all available list_ids
    """
    base_url = get_api_base_url_v2()
    data = api.request(f"{base_url}/data/list_ids", access_token=access_token)
    data = pd.DataFrame.from_dict(data)

    observation_data = api.request(
        f"{base_url}/observation_json/list_ids",
        access_token=access_token,
    )
    observation_data = pd.DataFrame.from_dict(observation_data)

    series_df = pd.concat([data, observation_data]).drop_duplicates()
    series_df = series_df.sort_values(["series_id"]).reset_index(drop=True)
    if not sort:
        return series_df

    series_df["pre"] = series_df["series_id"].str.split("/", 1).str[0]
    series_df = pd.DataFrame.from_dict(
        series_df.groupby("pre")["series_id"].apply(list).to_dict(), orient="index"
    ).transpose()
    series_df = series_df[sorted(series_df.columns)]

    series_df = series_df.fillna("")
    return series_df.copy()


def list_prediction_ids(*, access_token: str = None):
    """List all the prediction series ids available.

    Example:
        >>> import archimedes
        >>> archimedes.list_prediction_ids()
                                     series_id
        0               PX/rk-nn-probabilities
        1   PX/rk-nn-direction-probabilities/U
        ..                                ...
        22                           PX/rk-901
        23                         PX/rk-naive
    """

    data = api.request(
        f"{get_api_base_url_v2()}/data/list_prediction_ids",
        access_token=access_token,
    )

    return pd.DataFrame.from_dict(data)
