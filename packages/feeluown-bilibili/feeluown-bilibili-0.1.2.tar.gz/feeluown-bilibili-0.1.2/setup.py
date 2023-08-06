# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fuo_bilibili', 'fuo_bilibili.api', 'fuo_bilibili.api.schema']

package_data = \
{'': ['*'], 'fuo_bilibili': ['assets/*']}

install_requires = \
['beautifulsoup4', 'cachetools', 'feeluown>=3.8.7', 'pycryptodomex']

entry_points = \
{'fuo.plugins_v1': ['bilibili = fuo_bilibili']}

setup_kwargs = {
    'name': 'feeluown-bilibili',
    'version': '0.1.2',
    'description': 'Bilibili provider for FeelUOwn player.',
    'long_description': None,
    'author': 'Bruce Zhang',
    'author_email': 'zttt183525594@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
