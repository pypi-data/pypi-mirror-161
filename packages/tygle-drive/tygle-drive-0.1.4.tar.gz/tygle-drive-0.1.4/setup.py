# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tygle_drive',
 'tygle_drive.rest',
 'tygle_drive.types',
 'tygle_drive.types.enums',
 'tygle_drive.types.enums.files',
 'tygle_drive.types.enums.permissions',
 'tygle_drive.types.enums.permissions.permission_details',
 'tygle_drive.types.resources',
 'tygle_drive.types.resources.files',
 'tygle_drive.types.resources.permissions',
 'tygle_drive.types.responses',
 'tygle_drive.types.responses.files']

package_data = \
{'': ['*']}

install_requires = \
['tygle>=0.1.3,<0.2.0']

setup_kwargs = {
    'name': 'tygle-drive',
    'version': '0.1.4',
    'description': '',
    'long_description': '# tygle-drive\n',
    'author': 'shmookoff',
    'author_email': 'shmookoff@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
