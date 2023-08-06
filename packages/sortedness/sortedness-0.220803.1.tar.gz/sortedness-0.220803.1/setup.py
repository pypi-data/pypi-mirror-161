# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sortedness', 'sortedness.evaluation']

package_data = \
{'': ['*']}

install_requires = \
['lange>=0.220727.5,<0.220728.0']

extras_require = \
{':python_version >= "3.8" and python_version < "3.11"': ['scipy>=1.8.1,<2.0.0']}

setup_kwargs = {
    'name': 'sortedness',
    'version': '0.220803.1',
    'description': 'Measures of projection quality',
    'long_description': None,
    'author': 'davips',
    'author_email': 'dpsabc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
