from typing import Any, Dict

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

import akerbp.mlpet.dataset as dataset
import akerbp.mlpet.utilities as utilities


class FeatureSelector(BaseEstimator, TransformerMixin):
    def __init__(self, keep_columns=None, drop_columns=None):
        self.keep_columns = keep_columns
        self.drop_columns = drop_columns

    def fit(self, X: pd.DataFrame, y: pd.DataFrame = None) -> "FeatureSelector":
        return self

    def transform(self, X: pd.DataFrame, y: pd.DataFrame = None) -> pd.DataFrame:
        if self.keep_columns is not None:
            X = X[self.keep_columns]
        if self.drop_columns is not None:
            X = X.drop(columns=self.drop_columns, axis=1)
        return X


class MLPetTransformer(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        ds: dataset.Dataset,
        train_kwargs: Dict[str, Dict[str, Any]] = None,
        test_kwargs: Dict[str, Dict[str, Any]] = None,
        verbose=False,
    ):
        self.ds = ds
        self.train_kwargs = train_kwargs
        self.test_kwargs = test_kwargs
        self.verbose = verbose

    def fit(self, X: pd.DataFrame, y: pd.DataFrame) -> "MLPetTransformer":
        """
        Purely an implementational function to adhere to the sklearn API. See
        docstring for fit_transform.

        Args:
            X (pd.DataFrame): feature set
            y (pd.DataFrame): label set
        """
        return self

    def fit_transform(
        self, X: pd.DataFrame = None, y: pd.DataFrame = None
    ) -> pd.DataFrame:
        """
        Performs the requested train preprocessing pipeline either via the kwargs
        passed at class instantiation or via the pipeline defined in the class
        connected Dataset's settings file.

        Args:
            X (pd.DataFrame - optional): feature set to be preprocessed.
                Defaults to None. If X=None, the transformers attempts to
                retrieve X from the df_original saved to the dataset class
            y (pd.DataFrame - optional): Preprocessing of the label column is
                **NOT** supported. This is by default set to None

        Returns:
            X (pd.DataFrame - optional): Preprocessed feature set
            y (pd.DataFrame - optional): Preprocessed label set
        """
        # Combine the sets for preprocessing
        if X is not None:
            df = X
        elif hasattr(self.ds, "df_original"):
            df = self.ds.df_original.copy()
        else:
            raise ValueError("No dataframe was provided to the transformer!")

        # Perform preprocessing
        if self.train_kwargs is not None:
            df = self.ds.preprocess(df, verbose=self.verbose, **self.train_kwargs)
        elif hasattr(self.ds, "preprocessing_pipeline"):
            df = self.ds.preprocess(
                df,
                verbose=self.verbose,
            )
        else:
            ValueError("No preprocessing kwargs were provided to the transformer!")

        # Retrieve X
        if self.ds.label_column in df:
            X, _ = utilities.feature_target_split(df, self.ds.label_column)
        else:
            X = df

        return X

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Perform the requested test preprocessing pipeline either via the kwargs
        passed at class instantiation or via the pipeline defined in the class
        connected Dataset's settings file.

        Args:
            X (pd.DataFrame): The test set to be preprocessed

        Returns:
            pd.DataFrame: The preprocessed test set
        """
        # Perform preprocessing
        if self.test_kwargs is not None:
            X = self.ds.preprocess(X, verbose=self.verbose, **self.test_kwargs)
        elif hasattr(self.ds, "preprocessing_pipeline"):
            X = self.ds.preprocess(X, verbose=self.verbose)
        else:
            ValueError("No preprocessing kwargs were provided to the transformer!")
        return X
