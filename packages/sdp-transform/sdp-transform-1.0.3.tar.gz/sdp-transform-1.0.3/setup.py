# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sdp_transform']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sdp-transform',
    'version': '1.0.3',
    'description': 'A simple Python parser and writer of SDP.',
    'long_description': None,
    'author': 'Jiang Yue',
    'author_email': 'maze1024@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.0',
}


setup(**setup_kwargs)
