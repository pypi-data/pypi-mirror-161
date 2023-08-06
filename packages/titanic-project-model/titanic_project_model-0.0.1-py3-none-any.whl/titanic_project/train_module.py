"""
Creating Working dataframe
Define algorithm to analyse data
"""


import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression

from titanic_project.processing import data_processing
from titanic_project.config import settings


def train():
    """
    load data
    define feature target columns
    fill None values
    one-hot encoding
    define X, y as np.array (from df_train)
    import and train Logistic Regression
    save algorithm
    """

    df_train = data_processing.load_data()

    df_train = data_processing.preprocessing_data(df_train)
    df_train = df_train[settings.PROCESSED_FEATURES_COL + settings.TARGET_COL]

    # print(df_train)

    X = df_train[settings.PROCESSED_FEATURES_COL].values
    y = df_train[settings.TARGET_COL].values.ravel()

    clf = train_algorithm(X, y)

    joblib.dump(clf, settings.MODEL_PATH)


def train_algorithm(X: np.ndarray, y: np.ndarray):
    clf = LogisticRegression()
    clf.fit(X, y)
    return clf
