import pandas as pd


from ...abstract import AbstractNode
from ...models import DataContainer
from ...models import DataFramePivotFields
from ...models import DefaultValues


_PIVOT_FIELDS = DataFramePivotFields()
_DEFAULT_VALUES = DefaultValues()
_GROUP_COLUMNS = [
    _PIVOT_FIELDS.source_vehicle_id,
    _PIVOT_FIELDS.projected_date,
]
_AGG_COLUMN = "n_records"
_AGG_PARAMS = {
    _AGG_COLUMN: (_PIVOT_FIELDS.source_vehicle_id, "count"),
}
_GPS_SUFFIX = f"_{_DEFAULT_VALUES.sjoin_gps_suffix}"
_PLAN_SUFFIX = f"_{_DEFAULT_VALUES.sjoin_plan_suffix}"
_ACTION_FIELD = "action_required"

_DEFAULT_ACTION_MSG = "Keep as is"
_ACTION_MSG_TMP = "Drop vehicle-date in "


class CoverageStatistics(AbstractNode):
    """
    Table describes how provided gps covers provided route plan and inverse
    """

    def fit(self, X: DataContainer, y=None):
        return self

    def __agg_data(self, X: pd.DataFrame):
        return X.groupby(_GROUP_COLUMNS).agg(**_AGG_PARAMS).reset_index()

    def __add_action_recommendation(
        self,
        X: pd.DataFrame,
        source_suffix: str,
        target_suffix: str,
    ):
        drop_message = f"{_ACTION_MSG_TMP} {target_suffix}"
        is_missing_gps = X[_AGG_COLUMN + source_suffix].isna()
        X.loc[is_missing_gps, _ACTION_FIELD] = drop_message
        return X

    def __init_action_recommendation(
        self,
        X: pd.DataFrame,
    ):
        X[_ACTION_FIELD] = _DEFAULT_ACTION_MSG
        return X

    def transform(self, X: DataContainer):
        _gps_agg = self.__agg_data(X.gps)
        _plan_agg = self.__agg_data(X.plan)
        action_table = pd.merge(
            left=_gps_agg,
            right=_plan_agg,
            on=_GROUP_COLUMNS,
            how="outer",
            suffixes=[_GPS_SUFFIX, _PLAN_SUFFIX],
        )
        action_table = self.__init_action_recommendation(action_table)
        action_table = self.__add_action_recommendation(
            action_table,
            source_suffix=_GPS_SUFFIX,
            target_suffix=_PLAN_SUFFIX,
        )
        action_table = self.__add_action_recommendation(
            action_table,
            source_suffix=_PLAN_SUFFIX,
            target_suffix=_GPS_SUFFIX,
        )
        return action_table
