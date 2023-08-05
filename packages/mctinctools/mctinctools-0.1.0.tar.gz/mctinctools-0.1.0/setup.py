# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mctinctools']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mctinctools',
    'version': '0.1.0',
    'description': 'Common tools for our organization.',
    'long_description': '',
    'author': 'forums34',
    'author_email': 'greg.wendel@hey.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/forums34/mctinctools',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
