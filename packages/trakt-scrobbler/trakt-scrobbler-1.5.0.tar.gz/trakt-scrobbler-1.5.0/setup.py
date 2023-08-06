# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['trakt_scrobbler',
 'trakt_scrobbler.commands',
 'trakt_scrobbler.player_monitors']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'cleo>=0.8.1,<0.9.0',
 'confuse>=2.0,<3.0',
 'guessit>=3.3.1,<4.0.0',
 'requests>=2.25.1,<3.0.0',
 'urllib3>=1.26.0,<2.0.0',
 'urlmatch>=1.0.1,<2.0.0']

extras_require = \
{':sys_platform == "linux"': ['jeepney>=0.8,<0.9'],
 ':sys_platform == "win32"': ['pywin32>=227', 'win10toast>=0.9,<0.10'],
 'socks': ['pysocks>=1.7.1,<2.0.0']}

entry_points = \
{'console_scripts': ['trakts = trakt_scrobbler.console:main']}

setup_kwargs = {
    'name': 'trakt-scrobbler',
    'version': '1.5.0',
    'description': 'Scrobbler for trakt.tv that supports VLC, Plex, MPC-HC, and MPV',
    'long_description': '# Trakt Scrobbler\n\nA trakt.tv scrobbler for your computer.\n\n## What is Trakt?\n\nAutomatically scrobble TV show episodes and movies you are watching to [Trakt.tv](https://trakt.tv)! It is a website that keeps a history of everything you\'ve watched!\n\n## What is trakt-scrobbler?\n\n`trakt-scrobbler` is an application that runs in the background and monitors your media players for any new activity. When it detects some file being played, it determines the media info (such as name of the movie/show, episode number, etc.) and sends this to [trakt.tv](https://trakt.tv) servers, so that it can be marked as "Currently Watching" on your profile. No manual intervention required!\n\n## Features\n\n*   Full featured [command line interface](https://github.com/iamkroot/trakt-scrobbler/wiki/trakts-CLI-Reference) to control the service. Just run `trakts`.\n*   Automatic media info extraction using [guessit](https://github.com/guessit-io/guessit).\n*   Scrobbling is independent of the player(s) where the media is played. Support for new players can thus be easily added.\n*   Currently supports:\n    *   [VLC](https://www.videolan.org/vlc/) (via web interface)\n    *   [Plex](https://www.plex.tv) (doesn\'t require Plex Pass)\n    *   [MPV](https://mpv.io) (via IPC server)\n    *   [MPC-BE](https://sourceforge.net/projects/mpcbe/)/[MPC-HC](https://mpc-hc.org) (via web interface).\n*   **Folder whitelisting:** Only media files from subdirectories of these folders are synced with trakt.\n*   Optionally, you can receive a quick notification that the media start/pause/stop activity has been scrobbled.\n*   For cases when it misidentifies the files, you can specify a regex to manually extract the necessary details.\n*   Proxy support: Optionally specify a proxy server to handle all communication with trakt servers!\n\n## Getting Started\nHead over to the [wiki](https://github.com/iamkroot/trakt-scrobbler/wiki) for further details.\n\n## Contributing\n\nFeel free to create a new issue in case you find a bug/want to have a feature added. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for more details. Proper PRs are welcome.\n\n## Acknowledgements\n\n*   Inspired from [TraktForVLC](https://github.com/XaF/TraktForVLC)\n*   [mpv-trakt-sync-daemon](https://github.com/stareInTheAir/mpv-trakt-sync-daemon) was a huge help in making the mpv monitor\n',
    'author': 'iamkroot',
    'author_email': 'kroot.patel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/iamkroot/trakt-scrobbler',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
