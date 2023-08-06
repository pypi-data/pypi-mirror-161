"""
Function to predict result
"""


import pandas as pd
import joblib
from typing import Union

from titanic_project.config import settings
from titanic_project.processing import data_processing


def make_prediction(input_data: dict) -> Union[float, str]:
    """Make prediction based on input data"""
    clf = joblib.load(settings.MODEL_PATH)

    try:
        data_processing.validate_predict_data(input_data)
    except (ValueError or TypeError) as e:
        return f'Error: {e}'

    input_data_df = pd.DataFrame.from_dict(input_data)
    input_data_df = input_data_df[settings.FEATURES_COL]

    input_data_df = data_processing.preprocessing_data(input_data_df)
    input_data_df = input_data_df[settings.PROCESSED_FEATURES_COL]
    input_data_df = input_data_df.values

    prediction = clf.predict_proba(input_data_df)

    return prediction
