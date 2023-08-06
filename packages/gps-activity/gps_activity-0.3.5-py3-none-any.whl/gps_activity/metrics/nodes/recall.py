from ...abstract import AbstractNode
from ...models import DataContainer
from ...models import DataFramePivotFields


_PIVOT_FIELDS = DataFramePivotFields()
_PRIMARY_KEY = _PIVOT_FIELDS.plans_pk


class Recall(AbstractNode):
    def fit(self, X: DataContainer, y=None):
        return self

    def transform(self, X: DataContainer):
        n_plan_pkeys = X.plan[_PRIMARY_KEY].nunique()
        n_join_pkeys = X.clusters_plan_join[_PRIMARY_KEY].nunique()
        return n_join_pkeys / n_plan_pkeys
