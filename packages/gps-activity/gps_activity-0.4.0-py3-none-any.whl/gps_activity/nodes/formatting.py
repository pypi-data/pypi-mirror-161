from typing import List
import pandas as pd

from ..abstract import AbstractNode


class SelectColumns(AbstractNode):
    """
    Module selectng fields from dataframe
    """

    def __init__(self, columns: List[str]):
        self.columns = columns

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return X[self.columns]
