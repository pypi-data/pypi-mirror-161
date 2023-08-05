# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cookiecutter_aws']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cookiecutter-aws',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Adams Aliu',
    'author_email': 'aa2858@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
