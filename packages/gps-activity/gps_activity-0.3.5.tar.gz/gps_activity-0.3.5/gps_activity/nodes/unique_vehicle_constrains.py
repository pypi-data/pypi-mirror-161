from typing import List
import pandas as pd

from ..abstract import AbstractNode
from ..models import DataFramePivotFields


class UniqueVehicleConstrain(AbstractNode):
    """
    Module validating constrain that only one unique
    vehicle must be listed in dataframe
    """

    def __init__(
        self,
        pivot_fields: DataFramePivotFields,
    ):
        self.pivot_fields = pivot_fields

    def fit(self, X, y=None):
        return self

    @property
    def vehicle_id(self):
        return self.pivot_fields.source_vehicle_id

    def __is_more_than_one_vehicle(self, X: pd.DataFrame) -> bool:
        return X[self.vehicle_id].nunique() > 1

    def __get_vehicles(self, X: pd.DataFrame) -> List[str]:
        return list(X[self.vehicle_id].unique())

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.__is_more_than_one_vehicle(X):
            vehicles = self.__get_vehicles(X)
            message = f"More than one vehicle has been met in input data: {vehicles}"
            raise ValueError(message)
        return X
