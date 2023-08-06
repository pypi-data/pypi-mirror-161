# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['click_prompt']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.4', 'questionary>=1.10.0,<2.0.0']

setup_kwargs = {
    'name': 'click-prompt',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Markus Grotz',
    'author_email': 'grotz@uw.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.9,<4.0',
}


setup(**setup_kwargs)
