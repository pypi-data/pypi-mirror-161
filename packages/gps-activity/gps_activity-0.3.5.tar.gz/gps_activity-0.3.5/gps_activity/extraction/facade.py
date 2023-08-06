import pandas as pd
from sklearn.pipeline import Pipeline

from ..abstract import AbstractPredictor
from ..models import DataFramePivotFields


pivot_fields = DataFramePivotFields()


class ActivityExtractionSession(AbstractPredictor):
    """
    Class organizing life-cycle of activity extraction from
    GPS data  into form of session.

    Limitations:
    * 1 ActivityExtractionSession ~ 1 Vehicle
    * All components must be part of ecosystem
        `gps_activity_extraction.factory` module
    """

    def __init__(
        self,
        preprocessing: Pipeline,
        fragmentation: Pipeline,
        clustering: Pipeline,
        classification: Pipeline = None,
    ):
        """
        Args:
        preprocessing: Preprocessing pipeline module
        fragmentation: Fragmentation pipeline module
        clustering: Clustering pipeline module
        classification: CLassification pipeline module
        """
        self.preprocessing = preprocessing
        self.fragmentation = fragmentation
        self.clustering = clustering
        self.classification = classification

    def fit(self, X, y=None):
        return self

    def __preprocess_inputs(self, X: pd.DataFrame) -> pd.DataFrame:
        return self.preprocessing.transform(X)

    def __execute_fragmention(self, X: pd.DataFrame) -> pd.DataFrame:
        target_col = pivot_fields.fragmentation_output
        X[target_col] = self.fragmentation.predict(X)
        return X

    def __execute_clustering(self, X: pd.DataFrame) -> pd.DataFrame:
        target_col = pivot_fields.clustering_output
        X[target_col] = self.clustering.fit_predict(X)
        return X

    def __execute_classification(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.classification is not None:
            target_col = pivot_fields.classification_output
            X[target_col] = self.classification.predict(X)
        return X

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Clusters input dataframe by adding new columns

        Args:
        X: source dataframe

        Returns:
        pd.DataFrame: expanded dataframe
        """
        X = self.__preprocess_inputs(X)
        X = self.__execute_fragmention(X)
        X = self.__execute_clustering(X)
        X = self.__execute_classification(X)
        return X

    def get_fragmentation_input(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms data by the stage of entering to fragmentation module

        Args:
        X: source dataframe

        Returns:
        pd.DataFrame: transformed dataframe
        """
        X = self.__preprocess_inputs(X)
        return X

    def get_clustering_input(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms data by the stage of entering to clustering module

        Args:
        X: source dataframe

        Returns:
        pd.DataFrame: transformed dataframe
        """
        X = self.__preprocess_inputs(X)
        X = self.__execute_fragmention(X)
        return X

    def get_classification_input(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms data by the stage of entering to classification module

        Args:
        X: source dataframe

        Returns:
        pd.DataFrame: transformed dataframe
        """
        X = self.__preprocess_inputs(X)
        X = self.__execute_fragmention(X)
        X = self.__execute_clustering(X)
        return X
