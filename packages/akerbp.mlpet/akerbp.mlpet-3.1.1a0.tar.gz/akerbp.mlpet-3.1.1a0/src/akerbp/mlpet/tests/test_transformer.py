import os

import numpy as np
from numpy.testing import assert_array_almost_equal
from numpy.typing import NDArray
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_validate
from sklearn.pipeline import Pipeline

from akerbp.mlpet import Dataset
from akerbp.mlpet.tests.data.data import TRAIN_DF
from akerbp.mlpet.transformer import FeatureSelector, MLPetTransformer
from akerbp.mlpet.utilities import feature_target_split

SCORES: NDArray[np.float64] = np.array([-25.892382, -15.533893, -9.577987, -26.173846])
RANDOM_STATE = 42


def test_mlpet_transformer() -> None:
    ds = Dataset(
        mappings=os.path.abspath(r"src/akerbp/mlpet/tests/data/test_mappings.yaml"),
        settings=os.path.abspath(r"src/akerbp/mlpet/tests/data/test_settings.yaml"),
        folder_path=os.path.abspath(r"src/akerbp/mlpet/tests/data"),
    )

    mlpetTransformer = MLPetTransformer(ds)
    featureSelector = FeatureSelector(["RMED_gradient"])
    reg = RandomForestRegressor(random_state=RANDOM_STATE)

    pipeline = Pipeline(
        steps=[
            ["mlpet_transfomer", mlpetTransformer],
            ["selector", featureSelector],
            ["xgb_rgr", reg],
        ]
    )

    X, y = feature_target_split(TRAIN_DF, ds.label_column)

    kfold = KFold(n_splits=4)
    cv_results = cross_validate(
        pipeline,
        X,
        y,
        cv=kfold.split(X[ds.id_column]),
        scoring="neg_root_mean_squared_error",
        error_score="raise",
    )

    assert_array_almost_equal(cv_results["test_score"], SCORES)
