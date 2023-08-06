from sklearn.pipeline import Pipeline

from .. import nodes as local_nodes
from ... import nodes as global_nodes
from ...abstract import AbstractPipelineFactory
from ...models import DataFramePivotFields
from ...models import DefaultValues


class JoinValidatorFactory(AbstractPipelineFactory):
    @staticmethod
    def factory_pipeline(
        max_days_distance: int = 1,
        ensure_vehicle_overlap: bool = True,
    ) -> Pipeline:
        """
        Function creating instance of join
        validation pipeline of linker module

        Args:
        max_days_distance: Maximum temporal distance between
            plan and cluster join is allowed
        ensure_vehicle_overlap: if vehicle must be overlapped

        Returns:
        sklear.pipeline.Pipeline: Scikit-learn pipeline
        """
        default_fields = DataFramePivotFields()
        _default_values = DefaultValues()
        _gps_suffix = _default_values.sjoin_gps_suffix
        _plan_suffix = _default_values.sjoin_plan_suffix
        pivot_fields = DataFramePivotFields(
            source_lat=f"{default_fields.source_lat}_{_gps_suffix}",
            source_lon=f"{default_fields.source_lon}_{_gps_suffix}",
            projected_lat=f"{default_fields.source_lat}_{_plan_suffix}",
            projected_lon=f"{default_fields.source_lon}_{_plan_suffix}",
            source_datetime=f"{default_fields.projected_date}_{_gps_suffix}",
            source_vehicle_id=f"{default_fields.source_vehicle_id}_{_gps_suffix}",
        )
        return Pipeline(
            [
                (
                    "validator",
                    local_nodes.SpatialJoinValidator(
                        max_days_distance=max_days_distance,
                        ensure_vehicle_overlap=ensure_vehicle_overlap,
                    ),
                ),
                (
                    "schema_validator",
                    global_nodes.PanderaValidator(pivot_fields=pivot_fields),
                ),
                (
                    "columns_selector",
                    global_nodes.SelectColumns(
                        columns=[
                            pivot_fields.clusters_pk,
                            pivot_fields.plans_pk,
                            pivot_fields.sjoin_temporal_dist,
                            pivot_fields.sjoin_spatial_dist,
                            pivot_fields.sjoin_overall_dist,
                        ],
                    ),
                ),
            ],
        )
