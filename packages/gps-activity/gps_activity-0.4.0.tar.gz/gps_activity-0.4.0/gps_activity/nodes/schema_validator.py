import pandas as pd
from ..abstract import AbstractNode
from ..models import DataFramePivotFields


class PanderaValidator(AbstractNode):
    """
    Node performing validation of pandera schema
    """

    def __init__(self, pivot_fields: DataFramePivotFields):
        self.pandera_schema = pivot_fields.pandera_schema

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return self.pandera_schema.validate(X)
