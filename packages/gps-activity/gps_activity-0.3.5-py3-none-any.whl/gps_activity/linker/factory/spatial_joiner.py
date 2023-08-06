from typing import Literal, Union
from sklearn.pipeline import Pipeline

from .. import nodes as local_nodes
from ...abstract import AbstractPipelineFactory


class SpatialJoinerFactory(AbstractPipelineFactory):
    @staticmethod
    def factory_pipeline(
        how: Literal["left", "right", "inner", "outer"],
        max_distance: Union[float, int],
    ) -> Pipeline:
        """
        Function creating instance of spatial join
        instance pipeline of linker module

        Args:
        how: join method
        max_distance: maximum allowed distance between points
            of left & right dataframe to make a spatial join

        Returns:
        sklear.pipeline.Pipeline: Scikit-learn pipeline
        """
        return Pipeline(
            [
                (
                    "cluster_aggregator",
                    local_nodes.SpatialJoiner(
                        how=how,
                        max_distance=max_distance,
                    ),
                ),
            ],
        )
