import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from ...abstract import AbstractPredictor
from ...models import DataFramePivotFields
from ...models import DefaultValues


pivot_fields = DataFramePivotFields()
defaults = DefaultValues()


class FDBSCAN(AbstractPredictor):
    """
    Fragment Density Based Spatial Clustering, where
    fragmentation is selection of potential clustering candidates
    """

    SKIP_CANDIDATES_DEFAULT = defaults.noise_gps_cluster_id
    TEMP_CLUSTER_COL = pivot_fields.clustering_output

    # flake8: noqa: CFQ002
    def __init__(
        self,
        clustering_candidate_col: str,
        eps: float = 0.5,
        min_samples: float = 5,
        metric: str = "euclidean",
        metric_params=None,
        algorithm="auto",
        leaf_size=30,
        p=None,
        n_jobs=-1,
    ):
        self.clustering_candidate_col = clustering_candidate_col
        self.__dbscan = DBSCAN(
            eps=eps,
            min_samples=min_samples,
            metric=metric,
            metric_params=metric_params,
            algorithm=algorithm,
            leaf_size=leaf_size,
            p=leaf_size,
            n_jobs=n_jobs,
        )

    def __get_model_inputs(self, X: pd.DataFrame):
        return X.loc[self.__mask, self.__columns]

    def __extract_clustering_mask(self, X: pd.DataFrame):
        self.__mask = X[self.clustering_candidate_col].copy()

    def __extract_clustering_columns(self, X: pd.DataFrame):
        X = X.drop(columns=[self.clustering_candidate_col]).copy()
        self.__columns = list(X.columns)

    def fit(self, X: pd.DataFrame, y=None):
        self.__extract_clustering_mask(X)
        self.__extract_clustering_columns(X)

    def __impute_noise(self, X: pd.DataFrame) -> pd.DataFrame:
        column = self.TEMP_CLUSTER_COL
        X.loc[:, column] = X.loc[:, column].fillna(self.SKIP_CANDIDATES_DEFAULT)
        return X

    def __assign_predictions(self, X: pd.DataFrame, y: np.ndarray) -> pd.DataFrame:
        X.loc[self.__mask, self.TEMP_CLUSTER_COL] = y
        return X

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        y = self.__dbscan.fit_predict(self.__get_model_inputs(X))
        X = self.__assign_predictions(X=X, y=y)
        X = self.__impute_noise(X)
        return X[self.TEMP_CLUSTER_COL].values

    def fit_predict(self, X: pd.DataFrame, y=None):
        self.fit(X.copy(), y)
        return self.predict(X)
