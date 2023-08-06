# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bilimusic']

package_data = \
{'': ['*']}

install_requires = \
['eyed3>=0.9.6,<0.10.0',
 'fire>=0.4.0,<0.5.0',
 'moviepy>=1.0.3,<2.0.0',
 'pillow>=9.2.0,<10.0.0',
 'requests>=2.28.1,<3.0.0']

entry_points = \
{'console_scripts': ['bilimusic = bilimusic.cli:run']}

setup_kwargs = {
    'name': 'bilimusic',
    'version': '1.0.1',
    'description': 'BiliMusic helps you to download mp3 music file from bilibili video. Compared to a lot of same type applications and scripts, BiliMusic can do more, it can set metadata on mp3 file automatically.',
    'long_description': None,
    'author': 'aoout',
    'author_email': 'wuz66280@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<3.11',
}


setup(**setup_kwargs)
