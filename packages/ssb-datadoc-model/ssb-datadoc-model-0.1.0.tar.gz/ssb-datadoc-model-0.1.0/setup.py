# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datadoc_model']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'ssb-datadoc-model',
    'version': '0.1.0',
    'description': "Data Model for use in SSB's Metadata system",
    'long_description': None,
    'author': 'Bjørn Roar Joneid',
    'author_email': 'bnj@ssb.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
