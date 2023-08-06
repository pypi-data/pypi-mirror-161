# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['calixa_proto_py', 'calixa_proto_py.sidedata']

package_data = \
{'': ['*']}

install_requires = \
['googleapis-common-protos>=1.52,<2.0',
 'grpcio-tools>=1.30,<2.0',
 'mypy-protobuf>=1.23,<2.0']

entry_points = \
{'console_scripts': ['proto-gen = proto_gen:generate']}

setup_kwargs = {
    'name': 'calixa-proto-py',
    'version': '2.0.12',
    'description': 'Calixa proto py',
    'long_description': None,
    'author': 'Calixa Platform Developers',
    'author_email': 'everyone@calixa.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
