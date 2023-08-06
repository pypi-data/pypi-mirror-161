from typing import Any, Dict, List
import pandas as pd

from ...abstract import AbstractNode
from ...models import DataFramePivotFields
from ...models import DefaultValues


_GPS_NOISE_CLUSTER_ID = DefaultValues().noise_gps_cluster_id


class ClusterAggregator(AbstractNode):
    def __init__(
        self,
        pivot_fields: DataFramePivotFields,
        drop_noise_cluster: bool = True,
    ):
        self.pivot_fields = pivot_fields
        self.drop_noise_cluster = drop_noise_cluster

    def fit(self, X: pd.DataFrame, y=None):
        return self

    @property
    def group_columns(self) -> List[str]:
        return [
            self.pivot_fields.source_vehicle_id,
            self.pivot_fields.projected_date,
            self.pivot_fields.clustering_output,
        ]

    @property
    def agg_columns(self) -> Dict[str, Any]:
        return {
            self.pivot_fields.source_lon: (self.pivot_fields.source_lon, "mean"),
            self.pivot_fields.source_lat: (self.pivot_fields.source_lat, "mean"),
            self.pivot_fields.projected_lon: (self.pivot_fields.projected_lon, "mean"),
            self.pivot_fields.projected_lat: (self.pivot_fields.projected_lat, "mean"),
        }

    def __drop_noise_cluster(self, X: pd.DataFrame) -> pd.DataFrame:

        if self.drop_noise_cluster:
            cluster_column = self.pivot_fields.clustering_output
            is_not_noise_cluster = X[cluster_column] != _GPS_NOISE_CLUSTER_ID
            X = X[is_not_noise_cluster].reset_index(drop=True)

        return X

    def transform(self, X: pd.DataFrame):
        _agg = X.groupby(self.group_columns).agg(**self.agg_columns).reset_index()
        return self.__drop_noise_cluster(_agg)
