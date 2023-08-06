from typing import Dict, List, Union

from sklearn.pipeline import Pipeline


from ... import nodes as local_nodes
from .... import nodes as global_nodes
from ....abstract import AbstractPipelineFactory
from ....models import DataFramePivotFields


class FDBSCANFactory(AbstractPipelineFactory):

    # flake8: noqa: CFQ002
    @staticmethod
    def factory_pipeline(
        source_vehicle_id_column: str,
        eps: float = 0.5,
        min_samples: float = 5,
        metric: str = "euclidean",
        metric_params=None,
        algorithm="auto",
        leaf_size=30,
        p=None,
        n_jobs=-1,
    ) -> Pipeline:
        """
        Function builds scikit-learn pipeline and accepts DBSCAN hyper parameters

        Args:
        eps: max distance to link a points to cluster
        min_samples: min amount of samples to form a cluster
        metric: metrics used for estimate
        metric_params: who knows
        algorithm: algorithm for model building
        leaf_size (int, optional): _description_. Defaults to 30.
        p (_type_, optional): _description_. Defaults to None.
        n_jobs (int, optional): _description_. Defaults to -1.

        Returns:
        sklear.pipeline.Pipeline: Scikit-learn clustering pipeline
        """
        pivot_fields = DataFramePivotFields(source_vehicle_id=source_vehicle_id_column)
        return Pipeline(
            [
                (
                    "unique_vehicle_constrain",
                    global_nodes.UniqueVehicleConstrain(pivot_fields=pivot_fields),
                ),
                (
                    "select_columns",
                    global_nodes.SelectColumns(
                        columns=[
                            pivot_fields.projected_lat,
                            pivot_fields.projected_lon,
                            pivot_fields.computed_unixtime,
                            pivot_fields.fragmentation_output,
                        ],
                    ),
                ),
                (
                    "clustering_fdbscan",
                    local_nodes.FDBSCAN(
                        clustering_candidate_col=pivot_fields.fragmentation_output,
                        eps=eps,
                        min_samples=min_samples,
                        metric=metric,
                        metric_params=metric_params,
                        algorithm=algorithm,
                        leaf_size=leaf_size,
                        p=leaf_size,
                        n_jobs=n_jobs,
                    ),
                ),
            ],
        )
