# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['calitp']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2<3.1.0',
 'gcsfs>=2022.5.0,<2023.0.0',
 'google-api-core>=1.32.0,<2.0.0dev',
 'google-cloud-bigquery-storage==2.14.1',
 'google-cloud-bigquery>=1.15.0,<3.0.0dev',
 'gtfs-realtime-bindings>=0.0.7,<0.0.8',
 'humanize>=4.2.3,<5.0.0',
 'pandas-gbq<0.15.0',
 'pandas>=1.3.3,<2.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'protobuf>=3.19.0,<4.0.0dev',
 'pydantic>=1.9.1,<2.0.0',
 'siuba>=0.3.0,<0.4.0',
 'sqlalchemy-bigquery>=1.4.4,<2.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'calitp',
    'version': '2022.7.28a0',
    'description': 'Shared code for the Cal-ITP data codebases',
    'long_description': None,
    'author': 'Andrew Vaccaro',
    'author_email': 'atvaccaro@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
