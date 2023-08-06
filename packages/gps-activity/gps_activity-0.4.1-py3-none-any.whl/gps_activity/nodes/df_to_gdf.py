import geopandas as gpd
import pandas as pd

from ..abstract import AbstractNode
from ..models import CRSProjectionModel
from ..models import DataFramePivotFields


class ConverterDataFrame2GeoDataFrame(AbstractNode):
    """
    Module performing projection of
    pd.DataFrame -> gpd.GeoDataFrame with `geometry` columns
    """

    def __init__(
        self,
        pivot_fields: DataFramePivotFields,
        crs_projection: CRSProjectionModel,
    ):
        self.pivot_fields = pivot_fields
        self.crs_projection = crs_projection

    def fit(self, X, y=None):
        return self

    def __factory_geometry(self, X: pd.DataFrame):
        return gpd.points_from_xy(
            X[self.pivot_fields.projected_lon],
            X[self.pivot_fields.projected_lat],
        )

    def __factory_geodataframe(
        self,
        X: pd.DataFrame,
        geometry: gpd.GeoSeries,
    ):
        return gpd.GeoDataFrame(
            X,
            geometry=geometry,
            crs=self.crs_projection.target_crs,
        )

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        geometry = self.__factory_geometry(X)
        X = self.__factory_geodataframe(X=X, geometry=geometry)
        return X
