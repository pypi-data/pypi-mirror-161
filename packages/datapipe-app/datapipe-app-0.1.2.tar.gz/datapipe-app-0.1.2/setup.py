# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datapipe_app']

package_data = \
{'': ['*'],
 'datapipe_app': ['frontend/*',
                  'frontend/static/css/*',
                  'frontend/static/js/*',
                  'frontend/static/media/*']}

install_requires = \
['click>=7.1.2',
 'datapipe-core>=0.11.0-beta.7,<0.12',
 'fastapi>=0.78.0,<0.79.0',
 'uvicorn[standard]>=0.18.2,<0.19.0']

entry_points = \
{'console_scripts': ['datapipe = datapipe_app.cli:cli']}

setup_kwargs = {
    'name': 'datapipe-app',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'Andrey Tatarinov',
    'author_email': 'a@tatarinov.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
