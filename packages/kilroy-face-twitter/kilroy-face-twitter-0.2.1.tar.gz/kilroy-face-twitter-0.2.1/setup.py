# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['kilroy_face_twitter', 'kilroy_face_twitter.resources']

package_data = \
{'': ['*']}

install_requires = \
['asyncstdlib>=3.10,<4.0',
 'httpx>=0.23,<0.24',
 'kilroy-face-server-py-sdk>=0.5,<0.6',
 'tweepy[async]>=4.10,<5.0',
 'typer[all]>=0.6,<0.7']

extras_require = \
{'dev': ['pytest>=7.0,<8.0'], 'test': ['pytest>=7.0,<8.0']}

entry_points = \
{'console_scripts': ['kilroy-face-twitter = kilroy_face_twitter.__main__:cli']}

setup_kwargs = {
    'name': 'kilroy-face-twitter',
    'version': '0.2.1',
    'description': 'kilroy face for Twitter 🐦',
    'long_description': '<h1 align="center">kilroy-face-twitter</h1>\n\n<div align="center">\n\nkilroy face for Twitter 🐦\n\n[![Multiplatform tests](https://github.com/kilroybot/kilroy-face-twitter/actions/workflows/test-multiplatform.yml/badge.svg)](https://github.com/kilroybot/kilroy-face-twitter/actions/workflows/test-multiplatform.yml)\n[![Docker tests](https://github.com/kilroybot/kilroy-face-twitter/actions/workflows/test-docker.yml/badge.svg)](https://github.com/kilroybot/kilroy-face-twitter/actions/workflows/test-docker.yml)\n[![Docs](https://github.com/kilroybot/kilroy-face-twitter/actions/workflows/docs.yml/badge.svg)](https://github.com/kilroybot/kilroy-face-twitter/actions/workflows/docs.yml)\n\n</div>\n\n---\n\n## Installing\n\nUsing `pip`:\n\n```sh\npip install kilroy-face-twitter\n```\n',
    'author': 'kilroy',
    'author_email': 'kilroymail@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kilroybot/kilroy-face-twitter',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
