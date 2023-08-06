"""
Creating Global variables
"""

from pathlib import Path

import titanic_project


PACKAGE_ROOT = Path(titanic_project.__file__).resolve().parent
ROOT = PACKAGE_ROOT.parent
DATA_DIR_PATH = PACKAGE_ROOT / "data"
MODEL_DIR_PATH = PACKAGE_ROOT / "model"

TARGET_COL = ['Survived']
FEATURES_COL = ['Age', 'Sex', 'Embarked']
PROCESSED_FEATURES_COL = ['Age', 'Sex_female', 'Sex_male', 'Embarked_C', 'Embarked_Q', 'Embarked_S']
DATA_PATH = DATA_DIR_PATH / "train.csv"
MODEL_PATH = MODEL_DIR_PATH / "final_algorithm.pkl"
