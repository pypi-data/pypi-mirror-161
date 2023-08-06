# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['botbase', 'botbase.cogs', 'botbase.wraps']

package_data = \
{'': ['*']}

install_requires = \
['asyncpg>=0.25.0',
 'jishaku==2.4.0',
 'nextcord-ext-menus>=1.5.2,<2.0.0',
 'nextcord>=2.0.0-beta.2',
 'psutil>=5.9.0,<6.0.0']

entry_points = \
{'console_scripts': ['botbase = botbase.cli:main']}

setup_kwargs = {
    'name': 'ooliver-botbase',
    'version': '1.20.5',
    'description': 'A personal nextcord bot base package for bots.',
    'long_description': '# botbase\n\nThis is a bot base project for Discord python bots made with [nextcord](https://github.com/nextcord/nextcord) to reduce boilerplate.\n\n## Config values\n\n| Key                 | Type               | Default                                          |\n| ------------------- | ------------------ | ------------------------------------------------ |\n| `db_enabled`        | `bool`             | `True`                                           |\n| `db_url`            | `str`              |                                                  |\n| `db_name`           | `str`              |                                                  |\n| `db_user`           | `str`              | `"ooliver"`                                      |\n| `db_host`           | `str`              | `"localhost"`                                    |\n| `version`           | `str`              | `"0.0.0"`                                        |\n| `aiohttp_enabled`   | `bool`             | `True`                                           |\n| `colors`            | `list[int]`        | `[0x9966CC]`                                     |\n| `blacklist_enabled` | `bool`             | `True`                                           |\n| `prefix`            | `str \\| list[str]` | `None`                                           |\n| `helpmsg`           | `str`              | [`defaulthelpmsg`](botbase/botbase.py#L38-L47)   |\n| `helpindex`         | `str`              | [`defaulthelpindex`](botbase/botbase.py#L48-L50) |\n| `helptitle`         | `str`              | `"Help Me!"`                                     |\n| `helpfields`        | `dict[str, str]`   | `{}`                                             |\n| `helpinsert`        | `str`              | `""`                                             |\n| `emojiset`          | `Emojis[str, str]` | `Emojis[]`                                       |\n| `logchannel`        | `int`              | `None`                                           |\n| `guild_ids`         | `list[int]`        | `None`                                           |\n',
    'author': 'ooliver1',
    'author_email': 'oliverwilkes2006@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ooliver1/botbase',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
