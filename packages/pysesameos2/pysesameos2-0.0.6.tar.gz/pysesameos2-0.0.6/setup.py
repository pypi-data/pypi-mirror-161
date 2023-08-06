# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysesameos2', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['aenum>=3.1.11,<4.0.0',
 'bleak>=0.14.3,<0.15.0',
 'cryptography>=37.0.2,<38.0.0']

extras_require = \
{':python_version < "3.8"': ['typing-extensions>=4.2.0,<5.0.0',
                             'importlib-metadata>=4.11.4,<5.0.0'],
 'doc': ['livereload>=2.6.3,<3.0.0',
         'mkdocs>=1.3.0,<2.0.0',
         'mkdocstrings>=0.19.0,<0.20.0',
         'mkdocstrings-python>=0.7.0,<0.8.0',
         'mkdocs-autorefs>=0.4.1,<0.5.0',
         'mkdocs-include-markdown-plugin>=3.5.1,<4.0.0',
         'mkdocs-material>=8.2.15,<9.0.0']}

setup_kwargs = {
    'name': 'pysesameos2',
    'version': '0.0.6',
    'description': 'Unofficial library to control smart devices running Sesame OS2.',
    'long_description': "# pysesameos2\n\n_Unofficial Python Library to communicate with SESAME products via Bluetooth._\n\n[![PyPI](https://img.shields.io/pypi/v/pysesameos2)](https://pypi.python.org/pypi/pysesameos2)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pysesameos2)\n![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/mochipon/pysesameos2/dev%20workflow/main)\n[![Documentation Status](https://readthedocs.org/projects/pysesameos2/badge/?version=latest)](https://pysesameos2.readthedocs.io/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/mochipon/pysesameos2/branch/main/graph/badge.svg?token=EOkDeLXeG2)](https://codecov.io/gh/mochipon/pysesameos2)\n![PyPI - License](https://img.shields.io/pypi/l/pysesameos2)\n\n## Introduction\n\nThis project aims to control smart devices running **Sesame OS2** via **Bluetooth**. If you want to control them via the cloud service, please check [pysesame3](https://github.com/mochipon/pysesame3).\n\nTo be honest, this is my first time to use [`Bleak`](https://github.com/hbldh/bleak) which provides an asynchronous, cross-platform Bluetooth API. PRs are heavily welcome.\n\n* Free software: MIT license\n* Documentation: [https://pysesameos2.readthedocs.io](https://pysesameos2.readthedocs.io)\n\n## Tested Environments\n\n* macOS 10.15.7, Python 3.9.5\n* Raspberry Pi Zero W (Raspbian GNU/Linux 10, Raspberry Pi reference 2021-05-07), Python 3.7.3\n\n## Supported devices\n\n- [SESAME 3](https://jp.candyhouse.co/products/sesame3)\n- [SESAME 4](https://jp.candyhouse.co/products/sesame4)\n- [SESAME bot](https://jp.candyhouse.co/products/sesame3-bot)\n\n## Features\n\n* Scan all SESAME locks using BLE advertisements.\n* Receive state changes (locked, handle position, etc.) that are actively reported from the device.\n* Needless to say, locking and unlocking!\n\n## Consideration\n\n- The results of `pysesameos2` are merely from reverse engineering of [the official SDK](https://doc.candyhouse.co/). We have implemented just a small part of it, so you might run into some issues. Please do let me know if you find any problems!\n- `pysesameos2` only supports devices that have already been initially configured using the official app. That is, `pysesameos2` cannot configure the locking position of your device.\n- `pysesameos2` does not have, and will not have, any functionality related to the operation history of locks.  According to [the document](https://doc.candyhouse.co/ja/flow_charts#sesame-%E5%B1%A5%E6%AD%B4%E6%A9%9F%E8%83%BD), your lock's operation history is not stored in the lock itself, but on the cloud service. I personally recommend you to bring a Wi-Fi module to get the operation history uploaded and retrive it by [the API](https://doc.candyhouse.co/ja/SesameAPI#sesame%E3%81%AE%E5%B1%A5%E6%AD%B4%E3%82%92%E5%8F%96%E5%BE%97).\n\n## Usage\n\nPlease take a look at the [`example`](https://github.com/mochipon/pysesameos2/tree/main/example) directory.\n\n## Related Projects\n\n### Libraries\n| Name | Lang | Communication Method |\n----|----|----\n| [pysesame](https://github.com/trisk/pysesame) | Python | [Sesame API v1/v2](https://docs.candyhouse.co/v1.html)\n| [pysesame2](https://github.com/yagami-cerberus/pysesame2) | Python | [Sesame API v3](https://docs.candyhouse.co/)\n| [pysesame3](https://github.com/mochipon/pysesame3) | Python | [Web API](https://doc.candyhouse.co/ja/SesameAPI), [CognitoAuth (The official android SDK reverse-engineered)](https://doc.candyhouse.co/ja/android)\n| [pysesameos2](https://github.com/mochipon/pysesameos2) | Python | [Bluetooth](https://doc.candyhouse.co/ja/android)\n\n### Integrations\n| Name | Description | Communication Method |\n----|----|----\n| [doorman](https://github.com/jp7eph/doorman) | Control SESAME3 from Homebridge by MQTT | [Web API](https://doc.candyhouse.co/ja/SesameAPI)\n| [Doorlock](https://github.com/kishikawakatsumi/Doorlock) | iOS widget for Sesame 3 smart lock | [Web API](https://doc.candyhouse.co/ja/SesameAPI)\n| [gopy-sesame3](https://github.com/orangekame3/gopy-sesame3) | NFC (Felica) integration | [Web API](https://doc.candyhouse.co/ja/SesameAPI)\n| [homebridge-open-sesame](https://github.com/yasuoza/homebridge-open-sesame) | Homebridge plugin for SESAME3 | Cognito integration\n| [homebridge-sesame-os2](https://github.com/nzws/homebridge-sesame-os2) | Homebridge Plugin for SESAME OS2 (SESAME3) | [Web API](https://doc.candyhouse.co/ja/SesameAPI)\n| [sesame3-webhook](https://github.com/kunikada/sesame3-webhook) | Send SESAME3 status to specified url. (HTTP Post) | CognitoAuth (based on `pysesame3`)\n\n## Credits & Thanks\n\n* A huge thank you to all at [CANDY HOUSE](https://jp.candyhouse.co/) and their crowdfunding contributors!\n* Thanks to [@Chabiichi](https://github.com/Chabiichi)-san for [the offer](https://github.com/mochipon/pysesame3/issues/25) to get my SESAME bot!\n* Many thanks to [bleak](https://github.com/hbldh/bleak) and [pyzerproc](https://github.com/emlove/pyzerproc).\n",
    'author': 'Masaki Tagawa',
    'author_email': 'masaki@tagawa.email',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mochipon/pysesameos2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
