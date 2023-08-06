from typing import Dict, TypedDict

from pandas import Timestamp


class PredictionData(TypedDict):
    """
    Model for Prediction data
    """

    from_dt: Timestamp
    ref_dt: Timestamp
    run_dt: Timestamp
    data: Dict


class Prediction(PredictionData):
    """
    Model for Prediction
    """

    prediction_id: str
