import numpy as np
import pandas as pd

from ..abstract import AbstractNode
from ..models import DataFramePivotFields


class VelocityCalculator(AbstractNode):
    """
    Calculates velocity column from coordinates & time
    NOTE: given module is constrained over 1 velocity calculator = 1 vehicle
    """

    def __init__(
        self,
        pivot_fields: DataFramePivotFields,
    ):
        self.pivot_fields = pivot_fields

    def fit(self, X, y=None):
        return self

    def __get_l2_between_adjacent_points(self, X: pd.DataFrame) -> pd.DataFrame:
        lat_lon_columns = [self.pivot_fields.projected_lat, self.pivot_fields.projected_lon]
        lag_0_points = X.loc[:, lat_lon_columns]
        lag_1_points = X.loc[:, lat_lon_columns].shift(1)
        return lag_0_points - lag_1_points

    def __ensure_lack_time_duplicates(self, dt: pd.Series):
        if (dt == 0).any():
            raise ZeroDivisionError("Duplicated timestamps are met during computing velocity")

    def __get_unixtime_delta(self, X: pd.DataFrame) -> pd.DataFrame:
        unixtime_column = self.pivot_fields.computed_unixtime
        dt = X[unixtime_column] - X[unixtime_column].shift(1)
        dt = pd.Series(np.abs(dt))
        self.__ensure_lack_time_duplicates(dt)
        return dt

    def __sort_gps(self, X: pd.DataFrame) -> pd.DataFrame:
        sort_columns = [
            self.pivot_fields.source_vehicle_id,
            self.pivot_fields.computed_unixtime,
        ]
        X = X.sort_values(by=sort_columns)
        X.reset_index(drop=True, inplace=True)
        return X

    def __calculate_l2(self, dS: pd.DataFrame) -> pd.DataFrame:
        return np.sqrt((dS**2).T.sum())

    def __assign_velocity(
        self,
        X: pd.DataFrame,
        l2: pd.Series,
        dt: pd.Series,
    ) -> pd.DataFrame():
        X[self.pivot_fields.computed_velocity] = l2 / dt
        return X

    def __fillna_first(self, X: pd.DataFrame) -> pd.DataFrame:
        velocity_column = self.pivot_fields.computed_velocity
        X[velocity_column] = X[velocity_column].fillna(method="bfill")
        return X

    def __partition_over_vehicle_id(self, X: pd.DataFrame) -> pd.DataFrame:

        partitions = []
        vehicle_id_col = self.pivot_fields.source_vehicle_id

        for vehicle in X[vehicle_id_col].unique():
            _is_required_vehicle = X[vehicle_id_col] == vehicle
            _partition = X[_is_required_vehicle].reset_index(drop=True)
            partitions.append(_partition.copy())

        return partitions

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:

        X = self.__sort_gps(X)
        X = self.__partition_over_vehicle_id(X)

        dt = list(map(self.__get_unixtime_delta, X))
        dS = list(map(self.__get_l2_between_adjacent_points, X))

        l2 = list(map(self.__calculate_l2, dS))
        X = list(map(self.__assign_velocity, X, l2, dt))
        X = list(map(self.__fillna_first, X))

        X = pd.concat(X).reset_index(drop=True)

        return X
