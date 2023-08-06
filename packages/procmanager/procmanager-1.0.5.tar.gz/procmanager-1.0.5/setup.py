# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['procmanager']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['procmgr = procmanager:main']}

setup_kwargs = {
    'name': 'procmanager',
    'version': '1.0.5',
    'description': 'Helps starting & stopping programs',
    'long_description': None,
    'author': 'fdev31',
    'author_email': 'fdev31@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
