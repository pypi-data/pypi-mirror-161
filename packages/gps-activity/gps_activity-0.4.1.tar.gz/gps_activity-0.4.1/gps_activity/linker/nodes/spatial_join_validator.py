import logging
import numpy as np
import pandas as pd

from ...abstract import AbstractNode
from ...models import DataFramePivotFields
from ...models import DefaultValues


default_values = DefaultValues()
pivot_fields = DataFramePivotFields()
_VALID_FLAG_COL = pivot_fields.sjoin_valid_flag
_GPS_SUFFIX = default_values.sjoin_gps_suffix
_PLAN_SUFFIX = default_values.sjoin_plan_suffix


class SpatialJoinValidator(AbstractNode):
    """
    Module performing validation based on proximity between plan & gps locations
    NOTE: here is a corner case when no joins are found between GPS & Plan
    """

    DEFAULT_EMPTY_DATAFRAME = pd.DataFrame(
        {
            pivot_fields.sjoin_temporal_dist: [],
            pivot_fields.sjoin_spatial_dist: [],
            pivot_fields.sjoin_overall_dist: [],
        },
    )

    def __init__(
        self,
        max_days_distance: int,
        ensure_vehicle_overlap: bool = True,
    ):
        self.pivot_fields = DataFramePivotFields()
        self.ensure_vehicle_overlap = ensure_vehicle_overlap
        self.max_days_distance = max_days_distance

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def __init_validation_flag(self, X: pd.DataFrame) -> pd.DataFrame:
        X[_VALID_FLAG_COL] = True
        return X

    def __interpolate_colname(self, column: str, suffix: str) -> str:
        return f"{column}_{suffix}"

    @property
    def gps_date(self):
        date_col = self.pivot_fields.projected_date
        return self.__interpolate_colname(date_col, suffix=_GPS_SUFFIX)

    @property
    def plan_date(self):
        date_col = self.pivot_fields.projected_date
        return self.__interpolate_colname(date_col, suffix=_PLAN_SUFFIX)

    @property
    def gps_vehicle_id(self):
        vehicle_id = self.pivot_fields.source_vehicle_id
        return self.__interpolate_colname(vehicle_id, suffix=_GPS_SUFFIX)

    @property
    def plan_vehicle_id(self):
        vehicle_id = self.pivot_fields.source_vehicle_id
        return self.__interpolate_colname(vehicle_id, suffix=_PLAN_SUFFIX)

    def __calculate_days_distance(self, X: pd.DataFrame, gps_date: str, plan_date: str):
        delta_days = (X[gps_date] - X[plan_date]).dt.days
        return np.abs(delta_days)

    def __refresh_validation_flag(self, X: pd.DataFrame, validation_mask: pd.Series):
        X[_VALID_FLAG_COL] = X[_VALID_FLAG_COL] & validation_mask
        return X

    def __validate_temporal_tolerance(self, X: pd.DataFrame) -> pd.DataFrame:
        delta_days = self.__calculate_days_distance(
            X,
            gps_date=self.gps_date,
            plan_date=self.plan_date,
        )
        X[self.pivot_fields.sjoin_temporal_dist] = delta_days
        is_date_validated = delta_days <= self.max_days_distance
        X = self.__refresh_validation_flag(X, is_date_validated)
        return X

    def __validate_vehicle_overlap(self, X: pd.DataFrame) -> pd.DataFrame:
        are_vehicles_match = X[self.gps_vehicle_id] == X[self.plan_vehicle_id]
        X = self.__refresh_validation_flag(X, are_vehicles_match)
        return X

    def __apply_validations(self, X: pd.DataFrame) -> pd.DataFrame:
        X = self.__init_validation_flag(X)
        X = self.__validate_temporal_tolerance(X)
        X = self.__validate_vehicle_overlap(X)
        return X

    def __drop_joins_failed_validation(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.loc[X[self.pivot_fields.sjoin_valid_flag], :]
        X = X.reset_index(drop=True)
        return X

    def __get_temp_dist_weight(self, X: pd.DataFrame):
        return X[self.pivot_fields.sjoin_spatial_dist].max()

    def __get_spatial_dist_weight(self):
        return 1.0

    def __compute_weighted_overall_distance(self, X: pd.DataFrame) -> pd.DataFrame:
        _fields = self.pivot_fields
        X[_fields.sjoin_overall_dist] = (X[_fields.sjoin_temporal_dist] * self.__get_temp_dist_weight(X)) + (
            X[_fields.sjoin_spatial_dist] * self.__get_spatial_dist_weight()
        )
        return X

    def __sort_by_overall_distance(self, X: pd.DataFrame) -> pd.DataFrame:
        return X.sort_values(by=[self.pivot_fields.sjoin_overall_dist]).reset_index(drop=True)

    def __ensure_cardinality(self, X: pd.DataFrame):
        """
        Many jobs can be assigned to only one cluster
        One cluster can't be assinged to many job
        """
        return X.drop_duplicates(subset=[self.pivot_fields.plans_pk])

    def __is_has_any_cluster_plan_join(self, X: pd.DataFrame):
        return X.shape[0] > 0

    def __expand_empty_input_with_keys(self, X: pd.DataFrame):
        return pd.concat([X, self.DEFAULT_EMPTY_DATAFRAME], axis=1)

    def transform(self, X: pd.DataFrame):
        if self.__is_has_any_cluster_plan_join(X):
            X = self.__apply_validations(X)
            X = self.__drop_joins_failed_validation(X)
            X = self.__compute_weighted_overall_distance(X)
            X = self.__sort_by_overall_distance(X)
            X = self.__ensure_cardinality(X)
        else:
            logging.error("Provided session does't have any cluster-plan join")
            X = self.__expand_empty_input_with_keys(X)

        return X
