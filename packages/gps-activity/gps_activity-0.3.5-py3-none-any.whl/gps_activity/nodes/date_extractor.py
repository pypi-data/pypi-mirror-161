import pandas as pd

from ..abstract import AbstractNode
from ..models import DataFramePivotFields


class DateExtractor(AbstractNode):
    def __init__(
        self,
        pivot_fields: DataFramePivotFields,
    ):
        self.pivot_fields = pivot_fields

    def fit(self, X: pd.DataFrame, y=None):
        return self

    @property
    def datetime_column(self) -> str:
        return self.pivot_fields.source_datetime

    @property
    def date_column(self) -> str:
        return self.pivot_fields.projected_date

    def transform(self, X: pd.DataFrame):
        _datetimes = X[self.datetime_column]
        dates = pd.to_datetime(_datetimes).dt.date
        X[self.date_column] = dates
        return X
