from sklearn.pipeline import Pipeline

from .. import nodes as local_nodes
from ... import nodes as global_nodes
from ...abstract import AbstractPipelineFactory
from ...models import CRSProjectionModel
from ...models import DataFramePivotFields


class ClusterAggregationFactory(AbstractPipelineFactory):
    @staticmethod
    def factory_pipeline(
        source_lat_column: str,
        source_lon_column: str,
        source_datetime: str,
        source_vehicle_id: str,
        source_crs: str,
        target_crs: str,
    ) -> Pipeline:
        """
        Function creating instance of clustering
        instance pipeline of linker module

        Args:
        source_lat_column (str): source latitude
        source_lon_column (str): source longitude
        source_datetime (str): datetime
        source_vehicle_id (str): source vehicle identifier key
        source_crs (str): source coordinate reference system
        target_crs (str): target coordinate reference system

        Returns:
        sklear.pipeline.Pipeline: Scikit-learn pipeline
        """
        pivot_fields = DataFramePivotFields(
            source_lat=source_lat_column,
            source_lon=source_lon_column,
            source_datetime=source_datetime,
            source_vehicle_id=source_vehicle_id,
        )
        default_pivot_fields = DataFramePivotFields()
        projection_model = CRSProjectionModel(
            source_crs=source_crs,
            target_crs=target_crs,
        )
        return Pipeline(
            [
                (
                    "default_fields_projector",
                    global_nodes.DefaultSchemaProjector(
                        original_pivot_fields=pivot_fields,
                    ),
                ),
                (
                    "cluster_aggregator",
                    local_nodes.ClusterAggregator(default_pivot_fields),
                ),
                (
                    "dataframe_2_geodataframe",
                    global_nodes.ConverterDataFrame2GeoDataFrame(
                        pivot_fields=default_pivot_fields,
                        crs_projection=projection_model,
                    ),
                ),
                (
                    "primary_key_generator",
                    global_nodes.PrimaryKeyGenerator(
                        target_column=pivot_fields.clusters_pk,
                        source_columns=[
                            default_pivot_fields.source_vehicle_id,
                            default_pivot_fields.clustering_output,
                        ],
                    ),
                ),
            ],
        )
