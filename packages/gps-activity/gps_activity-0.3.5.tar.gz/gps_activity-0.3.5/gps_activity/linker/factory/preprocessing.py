from typing import List, Literal
from sklearn.pipeline import Pipeline

from ... import nodes as global_nodes
from ...abstract import AbstractPipelineFactory
from ...models import CRSProjectionModel
from ...models import DataFramePivotFields


_DEFAULTS = DataFramePivotFields()
_PK_MAPPINGS = {
    "gps": _DEFAULTS.gps_pk,
    "plan": _DEFAULTS.plans_pk,
}


class PreprocessingFactory(AbstractPipelineFactory):
    @staticmethod
    def validate_primary_key_literal(generate_primary_key_for):
        if generate_primary_key_for not in _PK_MAPPINGS.keys():
            raise ValueError(
                "Incorrect generate_primary_key_for which " f"must be one from {_PK_MAPPINGS.keys()}",
            )

    @staticmethod
    def choose_pk_field(generate_primary_key_for):
        return _PK_MAPPINGS[generate_primary_key_for]

    # flake8: noqa: CFQ002
    @staticmethod
    def factory_pipeline(
        source_lat_column: str,
        source_lon_column: str,
        source_datetime: str,
        source_vehicle_id: str,
        source_crs: str,
        target_crs: str,
        generate_primary_key_for: str,
        source_composite_keys: List[str],
    ) -> Pipeline:
        """
        Function creating instance of preprocessing
        instance pipeline of linker module

        Args:
        source_lat_column: source latitude
        source_lon_column: source longitude
        source_datetime: datetime
        source_vehicle_id: source vehicle identifier key
        source_crs: source coordinate reference system
        target_crs: target coordinate reference system
        generate_primary_key_for: determines for which datasource generate primary key
        source_composite_keys: source composite keys to generate primary key

        Returns:
        sklear.pipeline.Pipeline: Scikit-learn pipeline
        """

        PreprocessingFactory.validate_primary_key_literal(generate_primary_key_for)

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
        pk_field = PreprocessingFactory.choose_pk_field(
            generate_primary_key_for=generate_primary_key_for,
        )
        return Pipeline(
            [
                (
                    "schema_validator",
                    global_nodes.PanderaValidator(pivot_fields=pivot_fields),
                ),
                (
                    "primary_key_generator",
                    global_nodes.PrimaryKeyGenerator(
                        target_column=pk_field,
                        source_columns=source_composite_keys,
                    ),
                ),
                (
                    "default_fields_projector",
                    global_nodes.DefaultSchemaProjector(
                        original_pivot_fields=pivot_fields,
                    ),
                ),
                (
                    "date_extraction",
                    global_nodes.DateExtractor(
                        pivot_fields=default_pivot_fields,
                    ),
                ),
                (
                    "crs_projector",
                    global_nodes.CRSTransformer(
                        crs_projection=projection_model,
                        pivot_fields=default_pivot_fields,
                    ),
                ),
                (
                    "dataframe_2_geodataframe",
                    global_nodes.ConverterDataFrame2GeoDataFrame(
                        pivot_fields=default_pivot_fields,
                        crs_projection=projection_model,
                    ),
                ),
            ],
        )
