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
    'version': '0.1.1',
    'description': "Data Model for use in Statistics Norway's Metadata system",
    'long_description': "# ssb-datadoc-model\n\nData Model for use in Statistics Norway's Metadata system\n\n## Purpose\n\nThis package contains pydantic models defining the fields and data types used in Statistics Norway's metadata system. The purpose of these models is to:\n\n- Enable validation of user data\n- Enable serialization and deserialization of metadata files\n- Support versioning of the metadata format\n- Enforce consistency across multiple tools\n\n## Single Source of Truth\n\nFields and data types defined in models in this package are specified on internal Statistics Norway wiki pages:\n\n- <https://statistics-norway.atlassian.net/l/cp/kQ9rpshS>\n",
    'author': 'Statistics Norway',
    'author_email': 'mmw@ssb.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/statisticsnorway/ssb-datadoc-model',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
