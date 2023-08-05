# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sigma', 'sigma.backends.netwitness', 'sigma.pipelines.netwitness']

package_data = \
{'': ['*']}

install_requires = \
['pysigma>=0.6.4,<0.7.0']

setup_kwargs = {
    'name': 'pysigma-backend-netwitness',
    'version': '0.1.0',
    'description': 'pySigma Newtiness and Netwitness EPL backend',
    'long_description': None,
    'author': 'nNipsx',
    'author_email': 'nnipsxz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nNipsx-Sec/pySigma-backend-netwitness',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
