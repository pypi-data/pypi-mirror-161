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
    'version': '1.0.6',
    'description': 'Helps starting & stopping programs',
    'long_description': '# ProcManager\n\nAn command line to start and stop long-running processes.\n\n## Usage\n\nRun some program (`python -m http.server`) and keep track of it under the name **httpd**:\n```bash\nprocmgr start -n httpd python -m http.server\n```\n\nTo list currently running processes:\n\n```bash\nprocmgr list\n```\nTo remove track of no-longer running processes:\n\n```bash\nprocmgr clean\n```\nTo stop a running process:\n\n```bash\nprocmgr stop <name>\n```\n\n*if not specified, name defaults to the process name (first argument of start)*\n\nTo watch the output of some process:\n\n```bash\nprocmgr watch <name>\n```\n\n# Installation\n```pip install procmanager```\n',
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
