# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spotify_sync', 'spotify_sync.backup']

package_data = \
{'': ['*'], 'spotify_sync': ['data/*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'chump>=1.6.0,<2.0.0',
 'click-option-group>=0.5.3,<0.6.0',
 'click>=8.1.3,<9.0.0',
 'deezer-py>=1.3.7,<2.0.0',
 'flatdict>=4.0.1,<5.0.0',
 'jsonschema>=4.4.0,<5.0.0',
 'psutil>=5.9.0,<6.0.0',
 'requests>=2.25.1,<3.0.0',
 'spotipy>=2.19.0,<3.0.0',
 'ss-deemx>=3.6.8,<4.0.0',
 'tabulate>=0.8.7,<0.9.0']

extras_require = \
{':sys_platform == "windows"': ['pywin32>=304,<305']}

entry_points = \
{'console_scripts': ['spotify_sync = spotify_sync.__main__:cli']}

setup_kwargs = {
    'name': 'spot-sync',
    'version': '1.0.0',
    'description': 'A schedulable, configurable CLI downloader for Spotify accounts',
    'long_description': '# spotify_sync\n[![](https://img.shields.io/pypi/pyversions/spotify_sync)](https://pypi.org/project/spotify-sync/)\n[![](https://img.shields.io/badge/docs-%20-yellow)](https://docs.spotify-sync.jbh.cloud/)\n[![](https://img.shields.io/github/license/jbh-cloud/spotify_sync)](https://github.com/jbh-cloud/spotify_sync/blob/main/LICENSE.md)\n![](https://img.shields.io/github/stars/jbh-cloud/spotify_sync?style=social)\n\n![](run_example.gif)\n\n## Introduction\n\nspotify_sync is a CLI app written in Python that allows you to download songs from your Spotify account. It is designed to be a \'set and forget\' tool for users wanting to keep an offline copy of their songs.\n\n#### Features:\n\n* Download of liked songs\n* Download of playlist songs\n* Up-to lossless quality downloads\n* Multi-threaded downloading\n* Scheduling (e.g. cron)\n* Multi-config support; configure and schedule multiple profiles with separate Spotify accounts\n* Backup and restore of config and persistent data\n* Notification support via [Pushover](https://pushover.net/)\n* Automatic Plex library scanning via [Autoscan](https://github.com/Cloudbox/autoscan)\n\n\n## Requirements\n1. Python & pip >= 3.8\n2. Spotify account (Free)\n3. Deezer account (Free allows 128kbps downloads, up to lossless requires Deezer Hi-Fi account)\n\n\n## Install\n\n```\npython3 -m pip install -U spotify_sync\n```\n\n## Usage\n\n*Simple usage would be..*\n\nCache Spotify OAuth token\n```\nspotify_sync utils authorize-spotify --profile myFirstProfile\n```\n\nRun in automatic mode\n```\nspotify_sync run auto --profile myFirstProfile\n```\n\n### Documentation\n\nFurther configuration is required, details for which can be found at the [docs](https://docs.spotify-sync.jbh.cloud/).\n\n\n<a href="https://www.buymeacoffee.com/jbhcloud" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>\n\n\n### Disclaimer\n\nThis tool was written for educational purposes. I will not be responsible if you use this program in bad faith. By using it, you are accepting the [Deezer Terms of Use](https://www.deezer.com/legal/cgu).\n    spotify_sync is not affiliated with Deezer.\n',
    'author': 'JBH',
    'author_email': 'admin@jbh.cloud',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jbh-cloud/spotify_sync',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
