# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ibis_substrait',
 'ibis_substrait.compiler',
 'ibis_substrait.proto',
 'ibis_substrait.proto.substrait',
 'ibis_substrait.proto.substrait.extensions',
 'ibis_substrait.tests',
 'ibis_substrait.tests.compiler']

package_data = \
{'': ['*']}

install_requires = \
['ibis-framework>=2,<4',
 'packaging>=21.3,<22.0',
 'platformdirs<2.5.3',
 'protobuf>=3.19,<3.20']

setup_kwargs = {
    'name': 'ibis-substrait',
    'version': '2.9.5',
    'description': 'Subtrait compiler for ibis',
    'long_description': "# [Ibis](https://ibis-project.org) + [Substrait](https://substrait.io)\n\nThis repo houses the Substrait compiler for ibis.\n\nWe're just getting started here, so stay tuned!\n",
    'author': 'Ibis Contributors',
    'author_email': None,
    'maintainer': 'Ibis Contributors',
    'maintainer_email': None,
    'url': 'https://github.com/ibis-project/ibis-substrait',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
