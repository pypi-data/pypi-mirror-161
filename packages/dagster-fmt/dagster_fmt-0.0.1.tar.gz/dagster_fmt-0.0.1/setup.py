# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dagster_fmt',
 'dagster_fmt.ops',
 'dagster_fmt.resources',
 'dagster_fmt.shared',
 'dagster_fmt.tool']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dagster-fmt',
    'version': '0.0.1',
    'description': 'Dagster code gen tool',
    'long_description': None,
    'author': 'arudolph',
    'author_email': 'alex3rudolph@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
