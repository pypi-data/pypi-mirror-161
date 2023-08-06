# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'python'}

packages = \
['mugatu']

package_data = \
{'': ['*'],
 'mugatu': ['etc/*',
            'templates/dmode_check_w_dists.html',
            'templates/dmode_check_w_dists.html',
            'templates/dmode_check_w_dists.html',
            'templates/dmode_check_w_dists.html',
            'templates/dmode_check_w_dists.html',
            'templates/dmode_check_w_dists_sky.html',
            'templates/dmode_check_w_dists_sky.html',
            'templates/dmode_check_w_dists_sky.html',
            'templates/dmode_check_w_dists_sky.html',
            'templates/dmode_check_w_dists_sky.html',
            'templates/main_validation_page.html',
            'templates/main_validation_page.html',
            'templates/main_validation_page.html',
            'templates/main_validation_page.html',
            'templates/main_validation_page.html',
            'templates/valid_check.html',
            'templates/valid_check.html',
            'templates/valid_check.html',
            'templates/valid_check.html',
            'templates/valid_check.html',
            'templates/valid_check_w_dists.html',
            'templates/valid_check_w_dists.html',
            'templates/valid_check_w_dists.html',
            'templates/valid_check_w_dists.html',
            'templates/valid_check_w_dists.html']}

install_requires = \
['DateTime>=4.3,<5.0',
 'astropy>=5.1,<6.0',
 'fitsio>=1.0.5,<2.0.0',
 'jupyter>=1.0.0,<2.0.0',
 'notebook>=6.4.12,<7.0.0',
 'numpy>=1.19.5,<2.0.0',
 'ortools==9.1.9490',
 'scipy>=1.6.0,<2.0.0',
 'sdss-access==1.1.1',
 'sdss-coordio==1.2.1',
 'sdss-kaiju==1.2.2',
 'sdssdb>=0.5.4,<0.6.0']

setup_kwargs = {
    'name': 'sdss-mugatu',
    'version': '1.3.1',
    'description': 'Package to read, write and validate FPS designs',
    'long_description': '# mugatu\n\n![Versions](https://img.shields.io/badge/python->3.8-blue)\n[![Documentation Status](https://readthedocs.org/projects/mugatu/badge/?version=latest)](https://mugatu.readthedocs.io/en/latest/#)\n<!---\n[![Travis (.org)](https://img.shields.io/travis/sdss/mugatu)](https://travis-ci.org/sdss/mugatu)\n[![codecov](https://codecov.io/gh/sdss/mugatu/branch/main/graph/badge.svg)](https://codecov.io/gh/sdss/mugatu)\n-->\n\nPackage to read, write and validate FPS designs\n',
    'author': 'Ilija Medan',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/sdss-mugatu/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
