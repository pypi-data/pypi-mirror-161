# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['numina_data_client', 'numina_data_client.utils']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0',
 'gql>=3.4.0,<4.0.0',
 'imageio>=2.21.0,<3.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pyathena>=2.13.0,<3.0.0',
 's3fs>=2022.7.1,<2023.0.0',
 'shapely>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'numina-data-client',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Numina Engineering',
    'author_email': 'inquiries@numina.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
