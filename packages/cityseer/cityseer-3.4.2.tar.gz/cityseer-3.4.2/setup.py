
# -*- coding: utf-8 -*-
from setuptools import setup

import codecs

with codecs.open('README.md', encoding="utf-8") as fp:
    long_description = fp.read()
INSTALL_REQUIRES = [
    'matplotlib>=3.5.1',
    'networkx>=2.7.1',
    'pyproj>=3.3.0',
    'requests>=2.27.1',
    'scikit-learn>=1.0.2',
    'tqdm>=4.63.1',
    'utm>=0.7.0',
    'shapely>=1.8.2',
    'numba>=0.55.2',
    'numpy>=1.22.4',
    'numba-progress>=0.0.3',
    'geopandas>=0.10.2',
]

setup_kwargs = {
    'name': 'cityseer',
    'version': '3.4.2',
    'description': 'Computational tools for network-based pedestrian-scale urban analysis',
    'long_description': long_description,
    'license': 'AGPL-3.0',
    'author': '',
    'author_email': 'Gareth Simons <info@benchmarkurbanism.com>',
    'maintainer': '',
    'maintainer_email': 'Gareth Simons <info@benchmarkurbanism.com>',
    'url': 'https://cityseer.benchmarkurbanism.com/',
    'packages': [
        'cityseer',
        'demos',
        'cityseer.metrics',
        'cityseer.tools',
        'cityseer.algos',
        'demos.general_util',
        'demos.vae',
        'demos.vae.vae_util',
    ],
    'package_data': {'': ['*']},
    'long_description_content_type': 'text/markdown',
    'keywords': ['network-topology', 'numpy', 'architecture', 'openstreetmap', 'urban-planning', 'python3', 'networkx', 'networks', 'spatial-analysis', 'geographical-information-system', 'spatial-data', 'morphometrics', 'network-analysis', 'momepy', 'numba', 'spatial-data-analysis', 'centrality', 'shapely', 'landuse', 'osmnx', 'network-centralities'],
    'classifiers': [
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    'install_requires': INSTALL_REQUIRES,
    'python_requires': '>=3.8, <3.11',

}


setup(**setup_kwargs)
