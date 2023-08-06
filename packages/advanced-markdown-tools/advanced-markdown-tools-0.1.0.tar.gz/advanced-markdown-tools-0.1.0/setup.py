# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['markdown_tools']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.24.38,<2.0.0', 'click>=8.1.3,<9.0.0', 'requests>=2.28.1,<3.0.0']

entry_points = \
{'console_scripts': ['md_tools = markdown_tools.__main__:cli']}

setup_kwargs = {
    'name': 'advanced-markdown-tools',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Santiago Basulto',
    'author_email': 'santiago.basulto@gmail.com',
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
