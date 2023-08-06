import pandas as pd

from ..abstract import AbstractNode


class UnixtimeExtractor(AbstractNode):
    """
    Module adding unixtime to dataframe
    """

    SECONDS_DENOMINATOR = 10**9

    def __init__(
        self,
        source_column: str,
        target_column: str,
    ):
        self.source_column = source_column
        self.target_column = target_column

    def fit(self, X, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X[self.source_column] = pd.to_datetime(X[self.source_column])
        X[self.target_column] = X[self.source_column].astype(int) / self.SECONDS_DENOMINATOR
        return X
