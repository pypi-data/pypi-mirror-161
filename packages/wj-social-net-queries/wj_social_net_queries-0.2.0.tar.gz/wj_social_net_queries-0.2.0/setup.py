# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wj_social_net_queries',
 'wj_social_net_queries.connectors',
 'wj_social_net_queries.controllers',
 'wj_social_net_queries.core',
 'wj_social_net_queries.utils',
 'wj_social_net_queries.utils.constants']

package_data = \
{'': ['*']}

install_requires = \
['certifi==2022.6.15',
 'charset-normalizer==2.1.0',
 'idna==3.3',
 'numpy==1.21.1',
 'pandas==1.0.3',
 'python-dateutil==2.8.2',
 'python-dotenv==0.20.0',
 'pytz==2022.1',
 'requests==2.28.1',
 'six==1.16.0',
 'urllib3==1.26.11']

setup_kwargs = {
    'name': 'wj-social-net-queries',
    'version': '0.2.0',
    'description': "this library is responsible for comunicating with social network API's for data interaction with Whale and Jaguar products",
    'long_description': None,
    'author': 'w&j',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
