import pandas as pd

from . import nodes
from .models import Metrics
from ..abstract import AbstractNode
from ..models import DataContainer
from ..models import DataFramePivotFields


pivot_fields = DataFramePivotFields()


class ActivityMetricsSession(AbstractNode):
    """
    Class organizing sequence of computations of metrics of clustering data
    """

    DEFAULT_VALUE = -1
    NO_JOINS_STATUS_DETAILS = "No joins between clusters & plan"

    def __init__(
        self,
        beta: float = 1.0,
    ):
        """
        beta: beta argument parameter of fbeta score formula
        """
        self.beta = beta

    def fit(self, X, y=None):
        return self

    def __init_metrics_mapping(self):
        self.metrics_mappings = {
            "precision": nodes.Precision(),
            "recall": nodes.Recall(),
            "beta": self.beta,
            "fbeta_score": nodes.Fbeta(beta=self.beta),
        }

    def __compute_metric(self, X: pd.DataFrame, metric_key: str):
        self.metrics_mappings[metric_key] = self.metrics_mappings[metric_key].transform(X)

    def __is_has_any_cluster_plan_join(self, X: DataContainer):
        return X.clusters_plan_join.shape[0] > 0

    def transform(self, X: DataContainer) -> pd.DataFrame:
        if self.__is_has_any_cluster_plan_join(X):
            X.validated_coverage_stats()
            self.__init_metrics_mapping()
            self.__compute_metric(X, "precision")
            self.__compute_metric(X, "recall")
            self.__compute_metric(X, "fbeta_score")
            metrics = Metrics(**self.metrics_mappings)
        else:
            metrics = Metrics.factory_failure_metrics(
                beta=self.beta,
                status_details=self.NO_JOINS_STATUS_DETAILS,
            )

        return metrics
