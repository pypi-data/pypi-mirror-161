# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xklb']

package_data = \
{'': ['*']}

install_requires = \
['catt>=0.12.9,<0.13.0',
 'ipython>=8.4.0,<9.0.0',
 'joblib>=1.1.0,<2.0.0',
 'mutagen>=1.45.1,<2.0.0',
 'natsort>=8.1.0,<9.0.0',
 'pandas>=1.4.3,<2.0.0',
 'protobuf<4',
 'rich>=12.5.1,<13.0.0',
 'sqlite-utils>=3.28,<4.0',
 'subliminal>=2.1.0,<3.0.0',
 'tabulate>=0.8.10,<0.9.0',
 'tinytag>=1.8.1,<2.0.0']

entry_points = \
{'console_scripts': ['lb-extract = xklb.extract:main',
                     'lt = xklb.listen:main',
                     'wt = xklb.watch:main']}

setup_kwargs = {
    'name': 'xklb',
    'version': '0.1.2',
    'description': 'xk media library',
    'long_description': None,
    'author': 'Jacob Chapman',
    'author_email': '7908073+chapmanjacobd@users.noreply.github.com',
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
