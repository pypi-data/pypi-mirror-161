# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['toads']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'redis>=4.3.4,<5.0.0',
 'scikit-learn>=1.1.1,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'toads',
    'version': '0.1.4',
    'description': 'Data Science tools from preprocessing and visualization to statistics and ML',
    'long_description': None,
    'author': 'Ivan Rychkov',
    'author_email': 'rychkov.ivan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
