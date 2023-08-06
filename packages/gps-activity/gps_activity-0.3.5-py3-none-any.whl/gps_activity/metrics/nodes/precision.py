from ...abstract import AbstractNode
from ...models import DataContainer
from ...models import DataFramePivotFields


_PIVOT_FIELDS = DataFramePivotFields()
_PRIMARY_KEY = _PIVOT_FIELDS.clusters_pk


class Precision(AbstractNode):
    def fit(self, X: DataContainer, y=None):
        return self

    def transform(self, X: DataContainer):
        n_cluster_pkeys = X.clusters[_PRIMARY_KEY].nunique()
        n_join_pkeys = X.clusters_plan_join[_PRIMARY_KEY].nunique()
        return n_join_pkeys / n_cluster_pkeys
