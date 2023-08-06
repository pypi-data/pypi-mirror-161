# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fa_common',
 'fa_common.auth',
 'fa_common.db',
 'fa_common.licence',
 'fa_common.serializers',
 'fa_common.storage',
 'fa_common.workflow']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.0.1,<3.0.0',
 'aiohttp>=3.7.3,<4.0.0',
 'beanie>=1.9.2,<2.0.0',
 'email-validator>=1.1.2,<2.0.0',
 'fastapi>=0.73.0,<0.74.0',
 'humps>=0.2.2,<0.3.0',
 'loguru>=0.6.0,<0.7.0',
 'orjson>=3.4.7,<4.0.0',
 'pyparsing==2.4.7',
 'python-dateutil>=2.8.1,<3.0.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'python-jose>=3.2.0,<4.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'pytz>=2020.5,<2021.0',
 'six>=1.15.0,<2.0.0',
 'ujson>=5.1.0,<6.0.0']

extras_require = \
{'gcp': ['google-cloud-storage>=1.35.0,<2.0.0',
         'google-cloud-logging>=2.1.1,<3.0.0',
         'google-cloud-firestore>=2.0.2,<3.0.0',
         'firebase-admin>=4.5.1,<5.0.0'],
 'gitlab': ['oyaml>=1.0,<2.0', 'python-gitlab>=2.5.0,<3.0.0'],
 'minio': ['minio>=7.0.1,<8.0.0'],
 'rollbar': ['rollbar>=0.16.2,<0.17.0', 'httpx>=0.22.0,<0.23.0'],
 'secure': ['secure>=0.3.0,<0.4.0'],
 'windows': ['win32-setctime>=1.0.3,<2.0.0']}

setup_kwargs = {
    'name': 'fa-common',
    'version': '1.7.3',
    'description': 'CSIRO Geoanalytics FastAPI Common Framework. Standardises Data access, authentication, task execution and provides a number of utilities and helper classes.',
    'long_description': None,
    'author': 'Sam Bradley',
    'author_email': 'sam.bradley@csiro.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
