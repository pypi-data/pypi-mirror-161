# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asset_tracking', 'asset_tracking.database']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy-Utils>=0.38.3,<0.39.0',
 'SQLAlchemy>=1.3.0,<2.0.0',
 'argcomplete>=2.0.0,<3.0.0',
 'coloredlogs>=15.0.0,<16.0.0',
 'configparser>=5.2.0,<6.0.0',
 'pg8000>=1.29.1,<2.0.0',
 'pydantic>=1.8.0,<2.0.0',
 'python-dateutil>=2.8.0,<3.0.0']

entry_points = \
{'console_scripts': ['asset-tracker = asset_tracking.cli:main']}

setup_kwargs = {
    'name': 'asset-tracking',
    'version': '0.1.1',
    'description': 'Enterprise asset tracking by hostname for rouge device detection.',
    'long_description': None,
    'author': 'Sean McFeely',
    'author_email': 'mcfeelynaes@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
