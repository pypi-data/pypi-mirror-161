# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['cognite',
 'cognite.client',
 'cognite.client._api',
 'cognite.client._api.transformations',
 'cognite.client.data_classes',
 'cognite.client.data_classes.model_hosting',
 'cognite.client.data_classes.transformations',
 'cognite.client.utils']

package_data = \
{'': ['*']}

install_requires = \
['msal>=1,<2', 'requests>=2,<3', 'requests_oauthlib>=1,<2']

extras_require = \
{'all': ['sympy', 'pandas', 'geopandas>=0.10.0', 'shapely>=1.7.0'],
 'geo': ['geopandas>=0.10.0', 'shapely>=1.7.0'],
 'pandas': ['pandas'],
 'sympy': ['sympy']}

setup_kwargs = {
    'name': 'cognite-sdk',
    'version': '3.4.1',
    'description': 'Cognite Python SDK',
    'long_description': '<a href="https://cognite.com/">\n    <img src="https://github.com/cognitedata/cognite-python-docs/blob/master/img/cognite_logo.png" alt="Cognite logo" title="Cognite" align="right" height="80" />\n</a>\n\nCognite Python SDK\n==========================\n[![build](https://github.com/cognitedata/cognite-sdk-python/workflows/release/badge.svg)](https://github.com/cognitedata/cognite-sdk-python/actions?query=workflow:release)\n[![codecov](https://codecov.io/gh/cognitedata/cognite-sdk-python/branch/master/graph/badge.svg)](https://codecov.io/gh/cognitedata/cognite-sdk-python)\n[![Documentation Status](https://readthedocs.com/projects/cognite-sdk-python/badge/?version=latest)](https://cognite-docs.readthedocs-hosted.com/en/latest/)\n[![PyPI version](https://badge.fury.io/py/cognite-sdk.svg)](https://pypi.org/project/cognite-sdk/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\nThis is the Cognite Python SDK for developers and data scientists working with Cognite Data Fusion (CDF). \nThe package is tightly integrated with pandas, and helps you work easily and efficiently with data in Cognite Data \nFusion (CDF).\n\n## Documentation\n* [SDK Documentation](https://cognite-docs.readthedocs-hosted.com/en/latest/)\n* [API Documentation](https://doc.cognitedata.com/)\n* [Cognite Developer Documentation](https://docs.cognite.com/dev/)\n\n## Prerequisites\nIn order to start using the Python SDK, you need\n- Python3 (>= 3.8) and pip\n- An API key. Never include the API key directly in the code or upload the key to github. Instead, set the API key as an environment variable. See the usage example for how to authenticate with the API key.\n\nThis is how you set the API key as an environment variable on Mac OS and Linux:\n```bash\n$ export COGNITE_API_KEY=<your API key>\n```\n\nOn Windows, you can follows [these instructions](https://www.computerhope.com/issues/ch000549.htm) to set the API key as an environment variable.\n\n## Installation\n\n### without pandas or geopandas support\n\nTo install this package without pandas and geopandas support:\n```bash\n$ pip install cognite-sdk\n```\n\n### with pandas and geopandas support\n\nTo install with pandas, geopandas and shapely support.\n```bash\n$ pip install cognite-sdk[pandas, geo]\n```\n\n### Windows specific\n\nOn Windows, it is recommended to install `geopandas` and its dependencies using `conda` package manager,\nsee [geopandas installation page](https://geopandas.org/en/stable/getting_started/install.html#installation).\nThe following commands create a new environment, install `geopandas` and `cognite-sdk`.\n\n```bash\nconda create -n geo_env\nconda activate geo_env\nconda install --channel conda-forge geopandas\npip install cognite-sdk\n```\n\n## Examples\nFor a collection of scripts and Jupyter Notebooks that explain how to perform various tasks in Cognite Data Fusion (CDF) \nusing Python, see the GitHub repository [here](https://github.com/cognitedata/cognite-python-docs)\n\n## Changelog\nWondering about upcoming or previous changes to the SDK? Take a look at the [CHANGELOG](https://github.com/cognitedata/cognite-sdk-python/blob/master/CHANGELOG.md).\n\n## Contributing\nWant to contribute? Check out [CONTRIBUTING](https://github.com/cognitedata/cognite-sdk-python/blob/master/CONTRIBUTING.md).\n',
    'author': 'Erlend Vollset',
    'author_email': 'erlend.vollset@cognite.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
