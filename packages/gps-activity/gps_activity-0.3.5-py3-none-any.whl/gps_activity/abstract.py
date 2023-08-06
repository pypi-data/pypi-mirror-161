from abc import ABC, abstractmethod
from typing import List, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline


class AbstractNode(ABC, BaseEstimator, TransformerMixin):
    @abstractmethod
    def fit(self, X: pd.DataFrame, y=None):
        pass

    @abstractmethod
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        pass

    def fit_transform(self, X: pd.DataFrame, y=None):
        self.fit(X, y)
        return self.transform(X)


class AbstractPredictor(ABC, BaseEstimator, TransformerMixin):
    @abstractmethod
    def fit(self, X: pd.DataFrame, y=None):
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> Union[List[Union[int, float, str]], np.array]:
        pass

    def fit_predict(self, X: pd.DataFrame, y=None) -> Union[List[Union[int, float, str]], np.array]:
        self.fit(X, y)
        return self.predict(X)


class AbstractPipelineFactory(ABC):
    @staticmethod
    @abstractmethod
    def factory_pipeline(*args, **kwargs) -> Pipeline:
        pass
