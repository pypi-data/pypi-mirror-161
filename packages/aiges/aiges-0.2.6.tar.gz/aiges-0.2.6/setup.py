# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiges', 'aiges.backup', 'aiges.cmd', 'aiges.mywrapper.wrapper', 'aiges.utils']

package_data = \
{'': ['*'],
 'aiges': ['mywrapper/*', 'mywrapper/test_data/*', 'test_data/*', 'tpls/*']}

install_requires = \
['jinja2>=2.0']

setup_kwargs = {
    'name': 'aiges',
    'version': '0.2.6',
    'description': "A module for test aiges's python wrapper.py",
    'long_description': None,
    'author': 'maybaby',
    'author_email': 'ybyang7@iflytek.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
