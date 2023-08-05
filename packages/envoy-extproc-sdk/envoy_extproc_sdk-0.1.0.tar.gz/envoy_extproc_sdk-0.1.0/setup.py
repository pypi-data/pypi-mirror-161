# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['envoy_extproc_sdk', 'envoy_extproc_sdk.testing', 'envoy_extproc_sdk.util']

package_data = \
{'': ['*']}

install_requires = \
['datadog>=0.44.0,<0.45.0',
 'ddtrace',
 'grpcio>=1.46.1,<2.0.0',
 'grpclib>=0.4.2,<0.5.0',
 'protoc-gen-validate>=0.4.2,<0.5.0']

setup_kwargs = {
    'name': 'envoy-extproc-sdk',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'W. Ross Morrow',
    'author_email': 'morrowwr@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
