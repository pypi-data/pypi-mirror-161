# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cognite',
 'cognite.well_model',
 'cognite.well_model.client',
 'cognite.well_model.client.api',
 'cognite.well_model.client.api.merge_rules',
 'cognite.well_model.client.models',
 'cognite.well_model.client.utils',
 'cognite.well_model.wsfe']

package_data = \
{'': ['*']}

install_requires = \
['cognite-logger>=0.5.0,<0.6.0',
 'matplotlib>=3.4.3,<4.0.0',
 'msal>=1.13.0,<2.0.0',
 'nulltype>=2.3.1,<3.0.0',
 'numpy>=1.18.1,<2.0.0',
 'oauthlib>=3.1.0,<4.0.0',
 'pandas>=1.0.1,<2.0.0',
 'pydantic>=1.8,<2.0',
 'requests-oauthlib>=1.3.0,<2.0.0',
 'requests>=2.21.0,<3.0.0']

setup_kwargs = {
    'name': 'cognite-wells-sdk',
    'version': '0.14.9',
    'description': '',
    'long_description': '# Cognite Well Data Layer SDK\n\nCognite wells SDK is tool for interacting with the CDF Well Data Layer (WDL).\n\nThe well data layer (WDL) is an abstraction on top of CDF resources able to concatenate well data (wellhead, wellbores, trajectories, logs and other measurements, casings) from different sources into a single contextualized representation of the well that is independent of source and customer.\n\n# Usage\n\nPlease see [the documentation](https://cognite-wells-sdk.readthedocs-hosted.com/en/latest/) for usage.\n',
    'author': 'Sigurd Holsen',
    'author_email': 'sigurd.holsen@cognite.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
