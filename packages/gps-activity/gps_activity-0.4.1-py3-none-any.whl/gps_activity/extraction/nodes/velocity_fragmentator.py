from typing import Union
import pandas as pd


from ...abstract import AbstractPredictor


class VelocityFragmentator(AbstractPredictor):
    """
    Module selecting clustering candidates based on velocity value
    """

    def __init__(
        self,
        source_velocity_column: str,
        max_velocity_hard_limit: Union[float, int],
    ):
        self.source_velocity_column = source_velocity_column
        self.max_velocity_hard_limit = max_velocity_hard_limit

    def fit(self, X, y=None):
        return self

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        y = X[self.source_velocity_column] <= self.max_velocity_hard_limit
        return y.values
