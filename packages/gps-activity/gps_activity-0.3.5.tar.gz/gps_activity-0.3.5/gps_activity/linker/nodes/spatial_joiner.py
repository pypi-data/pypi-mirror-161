from typing import Union

from geopandas import gpd
import pandas as pd

from ...abstract import AbstractNode
from ...linker.models import SpatialJoinArguments
from ...models import DataFramePivotFields
from ...models import DefaultValues


defaults = DefaultValues()
pivot_fields = DataFramePivotFields()
_GPS_PREFIX = defaults.sjoin_gps_suffix
_PLAN_PREFIX = defaults.sjoin_plan_suffix
_L2_DISTANCE_COLUMN = pivot_fields.sjoin_spatial_dist


class SpatialJoiner(AbstractNode):
    def __init__(
        self,
        how: str = "inner",
        max_distance: Union[float, int] = 80,
    ):
        self.how = how
        self.max_distance = max_distance

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: SpatialJoinArguments):
        X.validate_tables()

        sjoin = gpd.sjoin_nearest(
            left_df=X.clustered_gps,
            right_df=X.route_plan,
            how=self.how,
            max_distance=self.max_distance,
            lsuffix=_GPS_PREFIX,
            rsuffix=_PLAN_PREFIX,
            distance_col=_L2_DISTANCE_COLUMN,
        )

        return sjoin
