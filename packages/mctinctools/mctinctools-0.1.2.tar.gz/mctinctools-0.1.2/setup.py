# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mctinctools']

package_data = \
{'': ['*']}

install_requires = \
['Faker>=13.15.1,<14.0.0',
 'Jinja2>=3.1.2,<4.0.0',
 'click>=8.1.3,<9.0.0',
 'mdx-gh-links>=0.3,<0.4',
 'mkdocs-material>=8.3.9,<9.0.0',
 'mkdocstrings-python>=0.7.1,<0.8.0',
 'mkdocstrings>=0.19.0,<0.20.0',
 'pandas>=1.4.3,<2.0.0',
 'pytest>=7.1.2,<8.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'rich>=12.5.1,<13.0.0']

setup_kwargs = {
    'name': 'mctinctools',
    'version': '0.1.2',
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
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
