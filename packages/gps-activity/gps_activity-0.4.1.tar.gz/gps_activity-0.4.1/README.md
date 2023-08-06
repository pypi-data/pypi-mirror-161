# **GPS activity** 🚛

A light-weight module for analysis of GPS activity. Package is designed to be trade-off solution for both researchers and developers in Waste Labs.

With `gps_activity` you can:

1. Cluster your time-series gps records to extract activity points
2. Join activity points with original plan or operation report
3. Estimate clustering performance

## Install

Using pip:

```bash
pip install gps_activity
```

## Extraction modules implementations 🔵 🟣 ⚫️

----

**[Overview extraction module components](https://github.com/WasteLabs/gps_activity/tree/main/docs/extraction/README.md)**

### VHFDBSCAN 🚀

* Fragmentation happens by hardlimiting of velocity computed from `lat,lon,datetime` columns
* Clustering conducted by classical DBSCAN

```python
from gps_activity import ActivityExtractionSession
from gps_activity.extraction.factory.preprocessing import PreprocessingFactory
from gps_activity.extraction.factory.fragmentation import VelocityFragmentationFactory
from gps_activity.extraction.factory.clustering import FDBSCANFactory


preprocessing = PreprocessingFactory.factory_pipeline(
    source_lat_column="lat",
    source_lon_column="lon",
    source_datetime="datetime",
    source_vehicle_id="plate_no",
    source_crs="EPSG:4326",
    target_crs="EPSG:2326",
)

fragmentation = VelocityFragmentationFactory.factory_pipeline(max_velocity_hard_limit=4)
clustering = FDBSCANFactory.factory_pipeline(eps=30, min_samples=3)

activity_extraction = ActivityExtractionSession(
    preprocessing=preprocessing,
    fragmentation=fragmentation,
    clustering=clustering,
)

activity_extraction.predict(gps)
```

## Linker module implementation 🔵 🟣 ⚫️

**[Overview linker module components](https://github.com/WasteLabs/gps_activity/tree/main/docs/linker/README.md)**


```python
# Initilize linkage components
from gps_activity import ActivityLinkageSession
from gps_activity.linker.factory import PreprocessingFactory
from gps_activity.linker.factory import ClusterAggregationFactory
from gps_activity.linker.factory import JoinValidatorFactory
from gps_activity.linker.factory import SpatialJoinerFactory
from gps_activity.linker.factory import CoverageStatisticsFactory


MAX_DISTANCE = 100
MAX_DAYS_DISTANCE = 1


gps_link_preprocess_pipeline = PreprocessingFactory.factory_pipeline(
    source_lat_column="lat",
    source_lon_column="lon",
    source_datetime="datetime",
    source_vehicle_id="plate_no",
    source_crs=WSG_84,
    target_crs=HK_CRS,
    generate_primary_key_for="gps",
    source_composite_keys=["plate_no", "datetime", "lat", "lon"],
)

plans_link_preprocess_pipeline = PreprocessingFactory.factory_pipeline(
    source_lat_column="lat",
    source_lon_column="lng",
    source_datetime="datetime",
    source_vehicle_id="re-assigned by Ricky",
    source_crs=WSG_84,
    target_crs=HK_CRS,
    generate_primary_key_for="plan",
    source_composite_keys=["CRN#"],
)

cluster_agg_pipeline = ClusterAggregationFactory.factory_pipeline(
    source_lat_column="lat",
    source_lon_column="lon",
    source_datetime="datetime",
    source_vehicle_id="plate_no",
    source_crs=WSG_84,
    target_crs=HK_CRS,
)

spatial_joiner = SpatialJoinerFactory.factory_pipeline(how="inner", max_distance=MAX_DISTANCE)
spatial_validator = JoinValidatorFactory.factory_pipeline(max_days_distance=MAX_DAYS_DISTANCE,
                                                          ensure_vehicle_overlap=True)
coverage_stats_extractor = CoverageStatisticsFactory.factory_pipeline()


gps_linker_session = ActivityLinkageSession(
    gps_preprocessor=gps_link_preprocess_pipeline,
    plan_preprocessor=plans_link_preprocess_pipeline,
    cluster_aggregator=cluster_agg_pipeline,
    spatial_joiner=spatial_joiner,
    spatial_validator=spatial_validator,
    coverage_stats_extractor=coverage_stats_extractor,
)


linker_results = gps_linker_session.transform({
    "gps": clustered_gps,
    "plan": plans,
})
```

## Metrics module implementation 📊

* **NOTE**: This module is highly experimental
* **NOTE**: This module depends on `linker` module

```python
from gps_activity.metrics import ActivityMetricsSession
from gps_activity.metrics.models import Metrics


metrics = ActivityMetricsSession(beta=2)
metrics = metrics.transform(linker_results)
```
