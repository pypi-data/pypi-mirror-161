# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skit_labels']

package_data = \
{'': ['*']}

install_requires = \
['aiobotocore>=2.1.2,<3.0.0',
 'aiofiles==0.8.0',
 'aiohttp==3.8.1',
 'attrs==20.3.0',
 'botocore>=1.23.24,<1.23.25',
 'dvc[s3]==2.9.5',
 'jsonschema==3.2.0',
 'loguru>=0.5.3,<0.6.0',
 'numpy==1.22.0',
 'pandas==1.4.2',
 'psycopg2-binary==2.9.3',
 'pydash>=5.1.0,<6.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'pytz==2021.1',
 'toml==0.10.2',
 'tqdm==4.62.1']

entry_points = \
{'console_scripts': ['skit-labels = skit_labels.cli:main']}

setup_kwargs = {
    'name': 'skit-labels',
    'version': '0.3.27',
    'description': 'Command line tool for interacting with labelled datasets at skit.ai.',
    'long_description': None,
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
