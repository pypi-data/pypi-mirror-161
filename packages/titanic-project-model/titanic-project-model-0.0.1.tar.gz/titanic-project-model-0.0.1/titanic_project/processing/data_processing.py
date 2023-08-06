"""
Helper functions to train model and maker prediction
"""


import pandas as pd

from titanic_project.config import settings


def load_data() -> pd.DataFrame:
    df_train = pd.read_csv(settings.DATA_PATH)

    # Adding GLOBAL variables
    df_train = df_train[settings.FEATURES_COL + settings.TARGET_COL]

    # fill None values
    df_train.dropna(inplace=True)

    return df_train


def preprocessing_data(df: pd.DataFrame) -> pd.DataFrame:
    """correct ordering of columns"""

    df_tmp = df.copy()

    # change the type of variables
    df_tmp['Age'] = df_tmp['Age'].astype('int32')

    # One-hot.
    df_tmp = pd.concat([pd.get_dummies(df_tmp['Sex'], prefix='Sex'), df_tmp], axis=1)
    df_tmp = pd.concat([pd.get_dummies(df_tmp['Embarked'], prefix='Embarked'), df_tmp], axis=1)

    for i in settings.PROCESSED_FEATURES_COL:
        if i not in df_tmp:
            df_tmp[i] = 0

    # if 'Sex_male' not in df_tmp:
    #     df_tmp['Sex_male'] = 0
    #
    # if 'Sex_female' not in df_tmp:
    #     df_tmp['Sex_female'] = 0
    #
    # if 'Embarked_S' not in df_tmp:
    #     df_tmp['Embarked_S'] = 0
    #
    # if 'Embarked_C' not in df_tmp:
    #     df_tmp['Embarked_C'] = 0
    #
    # if 'Embarked_Q' not in df_tmp:
    #     df_tmp['Embarked_Q'] = 0

    # drop categorical var - columns
    df_tmp.drop(columns=[
        'Sex',
        'Embarked'
    ], inplace=True)
    return df_tmp


def validate_predict_data(input_data: dict) -> None:

    if not all([True if type(x) in [int, float] else False for x in input_data['Age']]):
        raise TypeError('Non correct value (age)')

    elif not all([True if type(x) in [str] else False for x in input_data['Sex']]):
        raise TypeError('Non correct value (sex)')

    elif not all([True if type(x) in [str] else False for x in input_data['Embarked']]):
        raise TypeError('Non correct value (embarked)')

    for i in input_data['Sex']:
        if i not in ['female', 'male']:
            raise ValueError('Non correct value (sex)')

    for i in input_data['Embarked']:
        if i not in ['C', 'Q', 'S']:
            raise ValueError('Non correct value (embarked)')
