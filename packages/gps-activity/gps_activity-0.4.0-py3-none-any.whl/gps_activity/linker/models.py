from typing import Any
import geopandas as gpd
from pydantic import BaseModel

from ..models import DefaultValues


DEFAULT_VALUES = DefaultValues()


class SpatialJoinArguments(BaseModel):

    clustered_gps: Any
    route_plan: Any

    def __check_geometry(self, gdf: gpd.GeoDataFrame):
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise ValueError("Input dataframe is not instance of gpd.GeoDataFrame")
        if not ("geometry" in gdf.columns):
            raise ValueError("geometry column is missing in one of the source dataframe")

    def validate_tables(self):
        self.__check_geometry(self.clustered_gps)
        self.__check_geometry(self.route_plan)
