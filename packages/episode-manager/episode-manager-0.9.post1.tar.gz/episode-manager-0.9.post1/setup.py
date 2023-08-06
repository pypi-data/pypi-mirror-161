# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['episode_manager']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0']

entry_points = \
{'console_scripts': ['epm = episode_manager.epm:main']}

setup_kwargs = {
    'name': 'episode-manager',
    'version': '0.9.post1',
    'description': 'Keep track of your episode viewing and schedule.',
    'long_description': '# epm\n\nCommandline-based episode calendar/manager/scheduler/tracker (EPisode Manager)\n\nInspired by [Episode Calendar](https://episodecalendar.com).\n\n\n## Concepts\n\nSeries that have been added to epm can have one of these user states:\n\n- `planned`  Just added, nothing seen.\n- `started`  Some episodes seen, but not all.\n- `completed` All episodes seen but not archived (or explicitly restored).\n- `archived`  All episodes seen and series is "ended" or "cancelled". \n- `abandoned` Archived but only partially seen.\n\nMost of these states are implicit and automatic. \nHowever, the `archive` state can be manually controlled by the `archive` and `restore` commands.\n\nHow a series moves between the states is hopefully quite obvious when using the tool.\n\nHowever, a few "trickier" ones exist:\n\n- Command `mark`: If in `planned` moves to `started`. If it was the last episode (and the series is ended/cancelled), moves to `archived`.\n- Command `unmark`: If in `archived` moves to `started`. If no episode marked afterwards, moves to `planned`.\n\n\n## Dependencies\n\nRequires Python 3.9, because type hints are used (the lower-case variants).\n\n- [requests](https://pypi.org/project/requests)\n- [orjson](https://pypi.org/project/orjson) (optional)\n- `zstd` command-line tool. For compressing backups. (optional)\n- [API key for The Movie Database](https://www.themoviedb.org)\n\n<img alt="TMDb" src="https://www.themoviedb.org/assets/2/v4/logos/v2/blue_short-8e7b30f73a4020692ccca9c88bafe5dcb6f8a62a4c6bc55cd9ba82bb2cd95f6c.svg" width="50%">\n\n\n## File locations\n\nAll series and their states is stored in:\n\n    ~/.config/epm/\n\t\nMainly the file `series` but also numbered backups of it.\nIf this is important to you, it\'s recommended to backup this directory.\n\n## TMDb API key\n\nKey is read from the environment:\n\n    TMDB_API_KEY\n\n(it will soon also be configurable)\n\n## Examples\n\nNote, the exact appearance of these output examples might change. \nThey\'re continuously being tweaked and improved.\n\n\nAdd a series you\'d like to monitor:\n\n    > epm add twin peaks \n    Found 10 series:\n       #1 Twin Peaks                             1990-1991\n       #2 Twin Peaks                             2017-    \n       #3 Twin                                   2019-    \n       #4 Georgia Coffee: Twin Peaks             1993-    \n       #5 Twin Turbos                            2018-2020\n       #6 Twin Hawks                             1984-1985\n       #7 Twin of Brothers                       2004-    \n       #8 Lexi & Lottie: Trusty Twin Detectives  2016-2017\n       #9 Twin Hearts                            2003-2004\n      #10 Twin My Heart                          2019-    \n    Select series (1 - 10) to add --> 1    [user input]\n    Series added:  (series renumbered)\n       #1 Twin Peaks  1990-1991  tt0098936\n\nNow the series is added.\n\nAll added series can be listed by using the `list` / `ls` command:\n\n    > epm ls\n       #1 Twin Peaks              1990-1991  tt0098936\n           Total: Unseen: 30  1d 53min\n           Next: s1e01 Pilot  \n\nMark episodes that has been watched:\n\n    > epm mark 1 s1\n    Marked 8 episodes as seen:  7h\n       <list of episodes cut out>\n\n\t> epm mark 1 s2e1-20\n    Marked 20 episodes as seen:  16h 17min\n       <list of episodes cut out>\n\nThen, show current status, using no arguments (or the `unseen` command):\n\n    > epm\n       #1 Twin Peaks                                                                      1990-1991   1 unseen\n           Next:   s2e22 Episode #2.22                                                        46min 1991-06-10\n\n## Usage\n\n    epm / Episode Manager / (c)2022 André Jonsson\n    Version 0.7 (2022-07-19)\n    Usage: epm [<command>] [<args ...>]\n    \n    Where <command> is:  (one-letter alias highlighted)\n    search      Search for a series.\n    add         Search for a series and (optionally) add it.\n    delete      Complete remove a series - permanently!\n    list        List series\n    unseen      Show unseen episodes of series\n    mark        Mark a series, season or specific episode as seen.\n    unMark      Unmark a series/season/episode - reverse of mark command.\n    Archive     Archving series - hides from normal list command.\n    Restore     Restore series - reverse of archive command.\n    refresh     Refresh episode data of all non-archived series.\n    (none)  ▶  unseen\n    \n    See: epm <command> --help for command-specific help.\n    \n    Remarks:\n    # = Series listing number, e.g. as listed by the list command.\n    If an argument does not match a command, it will be used as argument to the default command.\n    Shortest unique prefix of a command is enough, e.g. "ar"  for "archive".\n    Using orjson for faster load/save.\n   \n\n',
    'author': 'André Jonsson',
    'author_email': 'pythonator@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
