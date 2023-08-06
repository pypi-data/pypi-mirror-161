# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gps_activity',
 'gps_activity.extraction',
 'gps_activity.extraction.factory',
 'gps_activity.extraction.factory.classifiers',
 'gps_activity.extraction.factory.clustering',
 'gps_activity.extraction.factory.fragmentation',
 'gps_activity.extraction.nodes',
 'gps_activity.linker',
 'gps_activity.linker.factory',
 'gps_activity.linker.nodes',
 'gps_activity.metrics',
 'gps_activity.metrics.nodes',
 'gps_activity.nodes']

package_data = \
{'': ['*']}

install_requires = \
['Rtree>=1.0.0,<2.0.0',
 'geopandas>=0.11.1,<0.12.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pandera>=0.11.0,<0.12.0',
 'pygeos>=0.12.0,<0.13.0',
 'scikit-learn>=1.1.1,<2.0.0',
 'scipy>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'gps-activity',
    'version': '0.4.1',
    'description': 'A light-weight mobile module for analysis of GPS activity',
    'long_description': '# **GPS activity** 🚛\n\nA light-weight module for analysis of GPS activity. Package is designed to be trade-off solution for both researchers and developers in Waste Labs.\n\nWith `gps_activity` you can:\n\n1. Cluster your time-series gps records to extract activity points\n2. Join activity points with original plan or operation report\n3. Estimate clustering performance\n\n## Install\n\nUsing pip:\n\n```bash\npip install gps_activity\n```\n\n## Extraction modules implementations 🔵 🟣 ⚫️\n\n----\n\n**[Overview extraction module components](https://github.com/WasteLabs/gps_activity/tree/main/docs/extraction/README.md)**\n\n### VHFDBSCAN 🚀\n\n* Fragmentation happens by hardlimiting of velocity computed from `lat,lon,datetime` columns\n* Clustering conducted by classical DBSCAN\n\n```python\nfrom gps_activity import ActivityExtractionSession\nfrom gps_activity.extraction.factory.preprocessing import PreprocessingFactory\nfrom gps_activity.extraction.factory.fragmentation import VelocityFragmentationFactory\nfrom gps_activity.extraction.factory.clustering import FDBSCANFactory\n\n\npreprocessing = PreprocessingFactory.factory_pipeline(\n    source_lat_column="lat",\n    source_lon_column="lon",\n    source_datetime="datetime",\n    source_vehicle_id="plate_no",\n    source_crs="EPSG:4326",\n    target_crs="EPSG:2326",\n)\n\nfragmentation = VelocityFragmentationFactory.factory_pipeline(max_velocity_hard_limit=4)\nclustering = FDBSCANFactory.factory_pipeline(eps=30, min_samples=3)\n\nactivity_extraction = ActivityExtractionSession(\n    preprocessing=preprocessing,\n    fragmentation=fragmentation,\n    clustering=clustering,\n)\n\nactivity_extraction.predict(gps)\n```\n\n## Linker module implementation 🔵 🟣 ⚫️\n\n**[Overview linker module components](https://github.com/WasteLabs/gps_activity/tree/main/docs/linker/README.md)**\n\n\n```python\n# Initilize linkage components\nfrom gps_activity import ActivityLinkageSession\nfrom gps_activity.linker.factory import PreprocessingFactory\nfrom gps_activity.linker.factory import ClusterAggregationFactory\nfrom gps_activity.linker.factory import JoinValidatorFactory\nfrom gps_activity.linker.factory import SpatialJoinerFactory\nfrom gps_activity.linker.factory import CoverageStatisticsFactory\n\n\nMAX_DISTANCE = 100\nMAX_DAYS_DISTANCE = 1\n\n\ngps_link_preprocess_pipeline = PreprocessingFactory.factory_pipeline(\n    source_lat_column="lat",\n    source_lon_column="lon",\n    source_datetime="datetime",\n    source_vehicle_id="plate_no",\n    source_crs=WSG_84,\n    target_crs=HK_CRS,\n    generate_primary_key_for="gps",\n    source_composite_keys=["plate_no", "datetime", "lat", "lon"],\n)\n\nplans_link_preprocess_pipeline = PreprocessingFactory.factory_pipeline(\n    source_lat_column="lat",\n    source_lon_column="lng",\n    source_datetime="datetime",\n    source_vehicle_id="re-assigned by Ricky",\n    source_crs=WSG_84,\n    target_crs=HK_CRS,\n    generate_primary_key_for="plan",\n    source_composite_keys=["CRN#"],\n)\n\ncluster_agg_pipeline = ClusterAggregationFactory.factory_pipeline(\n    source_lat_column="lat",\n    source_lon_column="lon",\n    source_datetime="datetime",\n    source_vehicle_id="plate_no",\n    source_crs=WSG_84,\n    target_crs=HK_CRS,\n)\n\nspatial_joiner = SpatialJoinerFactory.factory_pipeline(how="inner", max_distance=MAX_DISTANCE)\nspatial_validator = JoinValidatorFactory.factory_pipeline(max_days_distance=MAX_DAYS_DISTANCE,\n                                                          ensure_vehicle_overlap=True)\ncoverage_stats_extractor = CoverageStatisticsFactory.factory_pipeline()\n\n\ngps_linker_session = ActivityLinkageSession(\n    gps_preprocessor=gps_link_preprocess_pipeline,\n    plan_preprocessor=plans_link_preprocess_pipeline,\n    cluster_aggregator=cluster_agg_pipeline,\n    spatial_joiner=spatial_joiner,\n    spatial_validator=spatial_validator,\n    coverage_stats_extractor=coverage_stats_extractor,\n)\n\n\nlinker_results = gps_linker_session.transform({\n    "gps": clustered_gps,\n    "plan": plans,\n})\n```\n\n## Metrics module implementation 📊\n\n* **NOTE**: This module is highly experimental\n* **NOTE**: This module depends on `linker` module\n\n```python\nfrom gps_activity.metrics import ActivityMetricsSession\nfrom gps_activity.metrics.models import Metrics\n\n\nmetrics = ActivityMetricsSession(beta=2)\nmetrics = metrics.transform(linker_results)\n```\n',
    'author': 'Adil Rashitov',
    'author_email': 'adil@wastelab.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
