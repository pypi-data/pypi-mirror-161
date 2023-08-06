from typing import Dict
import pandas as pd
from sklearn.pipeline import Pipeline

from .models import SpatialJoinArguments
from ..abstract import AbstractNode
from ..models import DataContainer
from ..models import DataFramePivotFields


pivot_fields = DataFramePivotFields()


class ActivityLinkageSession(AbstractNode):
    """
    Class organizing sequence of computations of linkage
    source gps clusters & route plan details.
    NOTE: here is a corner case when no joins are found between GPS & Plan
    """

    GPS = "gps"
    PLAN = "plan"

    # flake8: noqa: CFQ002
    def __init__(
        self,
        gps_preprocessor: Pipeline,
        plan_preprocessor: Pipeline,
        cluster_aggregator: Pipeline,
        spatial_joiner: Pipeline,
        spatial_validator: Pipeline,
        coverage_stats_extractor: Pipeline,
    ):
        """
        gps_preprocessor: gps data preprocessing pipeline
        plan_reprocessing_pipeline: plan preprocessing pipeline
        cluster_aggregator: gps aggregation pipeline
        spatial_joiner: performs spatial join of clusters & route plan
        spatial_validator: performs spatial validation of cluster & route plan join
        coverage_stats_extractor: performs extraction of coverage
            gps & plan against each other
        """
        self.gps_preprocessor = gps_preprocessor
        self.plan_preprocessor = plan_preprocessor
        self.cluster_aggregator = cluster_aggregator
        self.spatial_joiner = spatial_joiner
        self.spatial_validator = spatial_validator
        self.coverage_stats_extractor = coverage_stats_extractor

    def fit(self, X, y=None):
        return self

    def __preprocess_gps(self, data_container: DataContainer):
        data_container.gps = self.gps_preprocessor.transform(data_container.gps)
        return data_container

    def __preprocess_plan(self, data_container: DataContainer):
        data_container.plan = self.plan_preprocessor.transform(data_container.plan)
        return data_container

    def __compute_coverage(self, data_container: DataContainer):
        data_container.coverage_stats = self.coverage_stats_extractor.transform(data_container)
        return data_container

    def __aggregate_clusters(self, data_container: DataContainer):
        data_container.clusters = self.cluster_aggregator.transform(data_container.gps)
        return data_container

    def __join_clusters_and_plan(self, data_container: DataContainer):
        # TODO: get rid from SpatialJoinArguments in favor direct pass of data_container
        sjoin_args = SpatialJoinArguments(
            clustered_gps=data_container.clusters,
            route_plan=data_container.plan,
        )
        data_container.clusters_plan_join = self.spatial_joiner.transform(sjoin_args)
        return data_container

    def __validate_joins(self, data_container: DataContainer):
        data_container.clusters_plan_join = self.spatial_validator.transform(data_container.clusters_plan_join)
        return data_container

    def compute_coverage_stats(self, X: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        data_container = DataContainer.factory_instance(X)
        data_container = self.__preprocess_gps(data_container)
        data_container = self.__preprocess_plan(data_container)
        data_container = self.__compute_coverage(data_container)
        return data_container.coverage_stats

    def transform(self, X: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        data_container = DataContainer.factory_instance(X)
        data_container = self.__preprocess_gps(data_container)
        data_container = self.__preprocess_plan(data_container)
        data_container = self.__compute_coverage(data_container)

        data_container = self.__aggregate_clusters(data_container)
        data_container = self.__join_clusters_and_plan(data_container)
        data_container = self.__validate_joins(data_container)
        return data_container
