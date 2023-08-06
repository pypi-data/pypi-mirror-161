# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['provworkflow']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.27,<4.0.0', 'rdflib>=6.1.1,<7.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'provworkflow',
    'version': '0.1.1',
    'description': 'A Python library for creating Workflows containing Blocks that log their actions according to a specialisation of the PROV-O standard.',
    'long_description': None,
    'author': 'nicholascar',
    'author_email': 'nicholas.car@surroundaustralia.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
