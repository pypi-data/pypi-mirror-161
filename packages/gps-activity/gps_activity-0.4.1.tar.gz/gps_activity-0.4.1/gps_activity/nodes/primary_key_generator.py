from typing import List
import pandas as pd

from ..abstract import AbstractNode
from ..models import DefaultValues


_KEYS_DELIMITER = DefaultValues().pk_delimiter


class PrimaryKeyGenerator(AbstractNode):
    """
    Module constructing single primary key from composite key
    """

    def __init__(
        self,
        target_column: str,
        source_columns: List[str],
    ):
        self.target_column = target_column
        if not isinstance(source_columns, list):
            raise ValueError("source columns must be list instance")
        self.source_columns = source_columns

    def fit(self, X, y=None):
        return self

    def __get_composite_key_fields(self, X: pd.DataFrame):
        _primary_key = X.loc[:, self.source_columns].astype(str).copy()
        return _primary_key

    def __expand_delimiters(self, X: pd.DataFrame) -> pd.DataFrame:
        X.iloc[:, :-1] = X.iloc[:, :-1] + _KEYS_DELIMITER
        return X

    def __assign_composite_key(self, X: pd.DataFrame, composite_keys: pd.Series):
        X.loc[:, self.target_column] = composite_keys.T.sum()
        return X

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        composite_keys = self.__get_composite_key_fields(X)
        composite_keys = self.__expand_delimiters(composite_keys)
        X = self.__assign_composite_key(X, composite_keys)
        return X
