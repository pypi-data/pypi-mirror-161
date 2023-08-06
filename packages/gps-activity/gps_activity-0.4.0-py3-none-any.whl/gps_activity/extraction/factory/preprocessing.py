from sklearn.pipeline import Pipeline

from ... import nodes as global_nodes
from ...abstract import AbstractPipelineFactory
from ...models import CRSProjectionModel
from ...models import DataFramePivotFields


class PreprocessingFactory(AbstractPipelineFactory):
    @staticmethod
    def factory_pipeline(
        source_lat_column: str,
        source_lon_column: str,
        source_datetime: str,
        source_vehicle_id: str,
        source_crs: str,
        target_crs: str,
    ) -> Pipeline:
        """Function creating instance of fragmentation module

        Args:
        source_lat_column (str): source latitude
        source_lon_column (str): source longitude
        source_datetime (str): datetime
        source_crs (str): source coordinate reference system
        target_crs (str): target coordinate reference system
        max_velocity_hard_limit (Union[float, int]): maximum velocity
            to consider as cluster candidate

        Returns:
        sklear.pipeline.Pipeline: Scikit-learn pipeline
        """
        pivot_fields = DataFramePivotFields(
            source_lat=source_lat_column,
            source_lon=source_lon_column,
            source_datetime=source_datetime,
            source_vehicle_id=source_vehicle_id,
        )
        projection_model = CRSProjectionModel(
            source_crs=source_crs,
            target_crs=target_crs,
        )
        return Pipeline(
            [
                (
                    "schema_validator",
                    global_nodes.PanderaValidator(pivot_fields=pivot_fields),
                ),
                (
                    "unique_vehicle_constrain",
                    global_nodes.UniqueVehicleConstrain(pivot_fields=pivot_fields),
                ),
                (
                    "crs_projector",
                    global_nodes.CRSTransformer(
                        crs_projection=projection_model,
                        pivot_fields=pivot_fields,
                    ),
                ),
                (
                    "unixtime_extractor",
                    global_nodes.UnixtimeExtractor(
                        source_column=pivot_fields.source_datetime,
                        target_column=pivot_fields.computed_unixtime,
                    ),
                ),
                (
                    "velocity_calculator",
                    global_nodes.VelocityCalculator(pivot_fields=pivot_fields),
                ),
            ],
        )
