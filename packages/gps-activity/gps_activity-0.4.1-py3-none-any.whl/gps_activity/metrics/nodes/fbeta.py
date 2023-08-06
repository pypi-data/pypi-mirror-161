from ...abstract import AbstractNode
from ...models import DataContainer
from ...models import DataFramePivotFields
from .precision import Precision
from .recall import Recall

_PIVOT_FIELDS = DataFramePivotFields()
_PRIMARY_KEY = _PIVOT_FIELDS.clusters_pk


class Fbeta(AbstractNode):
    def __init__(self, beta: float = 1):
        self.precision = Precision()
        self.recall = Recall()
        self.beta = beta

    def fit(self, X: DataContainer, y=None):
        return self

    def __fbeta(self, recall: float, precision: float, beta: float) -> float:
        _numerator = (1 + beta**2) * precision * recall
        _denominator = beta**2 * precision + recall
        return _numerator / _denominator

    def transform(self, X: DataContainer):
        _precision = self.precision.transform(X)
        _recall = self.recall.transform(X)
        fbeta_score = self.__fbeta(
            recall=_recall,
            precision=_precision,
            beta=self.beta,
        )
        return fbeta_score
