from typing import Dict, List, Tuple
import pandas as pd

from ..abstract import AbstractNode
from ..models import DataFramePivotFields


class DefaultSchemaProjector(AbstractNode):
    """
    Module projecting source user schema to default schema
    NOTE: this step is needed to work properly on fields at validation step
    """

    def __init__(
        self,
        original_pivot_fields: DataFramePivotFields,
    ):
        self.original_pivot_fields = original_pivot_fields
        self.target_pivot_fields = DataFramePivotFields()

    def fit(self, X, y=None):
        return self

    def __get_fields(self, pivot_fields: DataFramePivotFields) -> List[str]:
        return list(pivot_fields.__dict__.values())

    def __get_projection_candidates(self) -> Dict[str, str]:
        source_column_names = self.__get_fields(self.original_pivot_fields)
        target_column_names = self.__get_fields(self.target_pivot_fields)
        return list(zip(target_column_names, source_column_names))

    def __filter_pivot_field_overlaps(self, column_mapping: List[Tuple[str]]):
        projection_candidates = {}
        for target_column, source_column in column_mapping:
            if target_column != source_column:
                projection_candidates[target_column] = source_column
        return projection_candidates

    def __project_fields(
        self,
        X: pd.DataFrame,
        projection_mapping: Dict[str, str],
    ):
        for target_column, source_column in projection_mapping.items():
            X[target_column] = X[source_column]
        return X

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        projection_mapping = self.__get_projection_candidates()
        projection_mapping = self.__filter_pivot_field_overlaps(projection_mapping)
        X = self.__project_fields(X, projection_mapping)
        return X
