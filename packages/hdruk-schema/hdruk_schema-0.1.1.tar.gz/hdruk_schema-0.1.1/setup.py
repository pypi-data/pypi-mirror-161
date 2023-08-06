# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hdruk_schema']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'hdruk-schema',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Ibrahim Animashaun',
    'author_email': 'iaanimashaun@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
