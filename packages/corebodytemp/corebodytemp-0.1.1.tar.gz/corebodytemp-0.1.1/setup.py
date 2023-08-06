# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['corebodytemp']

package_data = \
{'': ['*']}

install_requires = \
['bleak>=0.14.0,<0.15.0']

setup_kwargs = {
    'name': 'corebodytemp',
    'version': '0.1.1',
    'description': 'Python BLE API for interacting with CoreBodyTemp Sensors',
    'long_description': '<h1 align="center">Welcome to corebodytemp 👋</h1>\n<p>\n  <img alt="Version" src="https://img.shields.io/badge/version-0.1.0-blue.svg?cacheSeconds=2592000" />\n  <a href="https://github.com/purpl3F0x/corebodytemp/blob/master/README.md" target="_blank">\n    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" />\n  </a>\n</p>\n\n> Python BLE API for interacting with CoreBodyTemp Sensors\n\n### 🏠 [Homepage](https://github.com/purpl3F0x/corebodytemp)\n\n## Install\n\n```sh\npip install corebodytemp\n```\n\n## Author\n\n👤 **Stavros Avramidis**\n\n* Github: [@purpl3F0x](https://github.com/purpl3F0x)\n\n## Show your support\n\nGive a ⭐️ if this project helped you!\n\n## 📝 License\n\nCopyright © 2022 [Stavros Avramidis](https://github.com/purpl3F0x).<br />\nThis project is [MIT](https://github.com/purpl3F0x/corebodytemp/blob/master/README.md) licensed.\n\n***\n',
    'author': 'Stavros Avramidis',
    'author_email': 'stavros9899@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/purpl3F0x/corebodytemp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
