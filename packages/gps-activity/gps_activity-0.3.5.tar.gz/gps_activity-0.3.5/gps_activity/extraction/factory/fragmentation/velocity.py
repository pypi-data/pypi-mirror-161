from sklearn.pipeline import Pipeline

from ... import nodes
from ....abstract import AbstractPipelineFactory
from ....models import DataFramePivotFields


pivot_fields = DataFramePivotFields()


_COMPUTED_VELOCITY_COLUMN = pivot_fields.computed_velocity


class VelocityFragmentationFactory(AbstractPipelineFactory):
    @staticmethod
    def factory_pipeline(
        max_velocity_hard_limit: int,
    ) -> Pipeline:
        """
        Args:
        max_velocity_hard_limit (int): maximum speed limit to be clustering candidate

        Returns:
        Pipeline: Scikit learn pipeline
        """
        return Pipeline(
            [
                (
                    "velocity_fragmentation",
                    nodes.VelocityFragmentator(
                        source_velocity_column=_COMPUTED_VELOCITY_COLUMN,
                        max_velocity_hard_limit=max_velocity_hard_limit,
                    ),
                ),
            ],
        )
