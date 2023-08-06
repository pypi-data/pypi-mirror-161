import pandas as pd
from pyproj import Transformer

from ..abstract import AbstractNode
from ..models import CRSProjectionModel
from ..models import DataFramePivotFields


class CRSTransformer(AbstractNode):
    """
    Module projecting coordinate reference system
    """

    def __init__(
        self,
        crs_projection: CRSProjectionModel,
        pivot_fields: DataFramePivotFields,
    ):
        self.crs_projection = crs_projection
        self.pivot_fields = pivot_fields
        self.crs_transformer = Transformer.from_crs(
            crs_projection.source_crs,
            crs_projection.target_crs,
            always_xy=True,
        )

    def fit(self, X, y=None):
        return self

    def __project_coordinates(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.crs_transformer.transform(
            df[self.pivot_fields.source_lon],
            df[self.pivot_fields.source_lat],
        )

    def __assign_projections(self, df, projection):
        df[self.pivot_fields.projected_lon] = projection[0]
        df[self.pivot_fields.projected_lat] = projection[1]
        return df

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        projection = self.__project_coordinates(X)
        X = self.__assign_projections(X, projection)
        return X
