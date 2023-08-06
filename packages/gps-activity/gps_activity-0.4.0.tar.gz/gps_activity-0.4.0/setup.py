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
    'version': '0.4.0',
    'description': 'A light-weight mobile module for analysis of GPS activity',
    'long_description': '# **Vehicle activity analysis** 🚛\n\nA light-weight module for analysis of GPS activity\n\n## **Waste Labs use cases** ♻️\n\n* 📈 **KPI monitoring**: clusters helps us to determine how much time vehicle spent on-site, how much it travelled\n* 📍 **Pick up locations verification**: helps to estimate if provided customer locations is groud truth\n\n---\n\n## **Navigation**\n\n* [GPS activity library modules](docs/gps_activity/README.md) 🚚 🚛 📍\n* [GPS activity extraction architectire](docs/gps_activity/extraction/README.md) ⚙️\n* [GPS activity extraction available models](docs/gps_activity/extraction/available_models/VHFDBSCAN/README.md) 🚀\n* [Performance dataset collection](docs/performance_dataset_collection/README.md) 🎯\n',
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
