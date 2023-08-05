# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pinefarm', 'pinefarm.cli', 'pinefarm.external', 'pinefarm.external.mg5']

package_data = \
{'': ['*'],
 'pinefarm': ['confs/*'],
 'pinefarm.external.mg5': ['cuts_code/*', 'cuts_variables/*', 'patches/*']}

install_requires = \
['PyYAML>=6.0.0,<7.0.0',
 'a3b2bbc3ced97675ac3a71df45f55ba>=6.4.0,<7.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'breezy>=3.2.1,<4.0.0',
 'click>=8.0.1,<9.0.0',
 'eko[box]>=0.9.4,<0.10.0',
 'lhapdf-management>=0.2,<0.3',
 'lz4>=3.1.3,<4.0.0',
 'more-itertools>=8.10.0,<9.0.0',
 'pandas>=1.3.0,<2.0.0',
 'pineappl==0.5.4',
 'pkgconfig>=1.5.5,<2.0.0',
 'pygit2>=1.6.1,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'rich>=12.5.1,<13.0.0',
 'tomli>=2.0.1,<3.0.0',
 'yadism>=0.11.3,<0.12.0']

extras_require = \
{'docs': ['Sphinx>=4.2.0,<5.0.0',
          'sphinx-rtd-theme>=1.0.0,<2.0.0',
          'sphinxcontrib-bibtex>=2.4.1,<3.0.0']}

entry_points = \
{'console_scripts': ['pinefarm = pinefarm:command']}

setup_kwargs = {
    'name': 'pinefarm',
    'version': '0.0.1',
    'description': 'Generate PineAPPL grids from PineCards.',
    'long_description': None,
    'author': 'Alessandro Candido',
    'author_email': 'candido.ale@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
