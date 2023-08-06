# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['watchmen_storage_s3']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.24.20,<2.0.0', 'watchmen-storage==16.3.3']

setup_kwargs = {
    'name': 'watchmen-storage-s3',
    'version': '16.3.3',
    'description': '',
    'long_description': None,
    'author': 'botlikes',
    'author_email': '75356972+botlikes456@users.noreply.github.com',
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
