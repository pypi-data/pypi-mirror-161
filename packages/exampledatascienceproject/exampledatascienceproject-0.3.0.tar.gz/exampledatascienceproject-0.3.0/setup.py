# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['exampledatascienceproject']

package_data = \
{'': ['*']}

install_requires = \
['pendulum>=2.1.2,<3.0.0']

setup_kwargs = {
    'name': 'exampledatascienceproject',
    'version': '0.3.0',
    'description': '',
    'long_description': None,
    'author': 'Leonard Schuler',
    'author_email': 'leonard.schuler@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
