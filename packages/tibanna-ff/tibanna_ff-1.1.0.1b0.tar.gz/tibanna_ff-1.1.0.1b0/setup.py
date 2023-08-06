# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['tibanna_4dn',
 'tibanna_4dn.lambdas',
 'tibanna_cgap',
 'tibanna_cgap.lambdas',
 'tibanna_ffcommon']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.9.0,<2.0.0',
 'botocore>=1.12.1,<2.0.0',
 'dcicutils>=3.5.0,<4.0.0',
 'requests>=2.22.0,<3.0.0',
 'tibanna>=2.0.0',
 'tomlkit>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['tibanna_4dn = tibanna_4dn.__main__:main',
                     'tibanna_cgap = tibanna_cgap.__main__:main']}

setup_kwargs = {
    'name': 'tibanna-ff',
    'version': '1.1.0.1b0',
    'description': 'Tibanna runs portable pipelines (in CWL/WDL) on the AWS Cloud.',
    'long_description': '# Tibanna_ff\n\nThis is an extension of Tibanna that integrates with 4DN/CGAP data portals.\n\n[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/) ![Build Status](https://travis-ci.com/4dn-dcic/tibanna_ff.svg?branch=master)\n\n\n',
    'author': '4DN-DCIC Team',
    'author_email': 'support@4dnucleome.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://github.com/4dn-dcic/tibanna_ff',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.9',
}


setup(**setup_kwargs)
