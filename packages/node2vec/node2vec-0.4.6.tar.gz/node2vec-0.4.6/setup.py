# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['node2vec']

package_data = \
{'': ['*']}

install_requires = \
['gensim>=4.1.2,<5.0.0',
 'joblib>=1.1.0,<2.0.0',
 'networkx>=2.5,<3.0',
 'numpy>=1.19.5,<2.0.0',
 'tqdm>=4.55.1,<5.0.0']

setup_kwargs = {
    'name': 'node2vec',
    'version': '0.4.6',
    'description': 'Implementation of the node2vec algorithm',
    'long_description': None,
    'author': 'elior',
    'author_email': 'elior.cohen.p@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/eliorc/node2vec',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
