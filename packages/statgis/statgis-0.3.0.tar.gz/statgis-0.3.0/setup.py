# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['statgis']

package_data = \
{'': ['*']}

install_requires = \
['earthengine-api>=0.1,<0.2', 'pandas>=1.3,<2.0']

setup_kwargs = {
    'name': 'statgis',
    'version': '0.3.0',
    'description': 'Functions for spatial data analysis developed by StatGIS.org',
    'long_description': '# Statgis Toolbox\n\n`statgis` is a Python package developed and maintained by StatGIS.org used to perform several spatial data science analysis.This package counts with function operate with Google Earth Engine.\n\nThe current version of statgis is 0.3.0.\n## Credits\n\nAll the attribution of the development and maintance of this package is for StatGIS.org and its developers team.\n',
    'author': 'Narváez, Sebástian',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
