# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yahoo_finance_cache']

package_data = \
{'': ['*']}

install_requires = \
['dateparser>=1.1.1,<2.0.0',
 'pandas-datareader>=0.10.0,<0.11.0',
 'pandas>=1.4.3,<2.0.0']

setup_kwargs = {
    'name': 'yahoo-finance-cache',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'IsaacBreen',
    'author_email': '57783927+IsaacBreen@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
