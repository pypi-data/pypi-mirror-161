# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tegracli']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'Telethon>=1.24.0,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'loguru>=0.6.0,<0.7.0',
 'pandas>=1.4.3,<2.0.0',
 'ujson>=5.4.0,<6.0.0']

entry_points = \
{'console_scripts': ['tegracli = tegracli.main:cli']}

setup_kwargs = {
    'name': 'tegracli',
    'version': '0.1.1',
    'description': 'A research-focused Telegram CLI application',
    'long_description': "# tegracli\n\nA convenience wrapper around Telethon and the Telegram Client API for research purposes.\n\n# Installation Instructions\n\n`tegracli` uses Poetry and python >= 3.9 for building and installing.\n\nTo install using pipx, run the following command `pipx install tegracli`.\n\n## How to get API keys\n\nIf you don't have API keys for Telegram, head over to [my.telegram.org](https://my.telegram.org). Click on [API development tools](https://my.telegram.org/apps), fill the form to create yourself an app and pluck the keys into `tegracli.conf.yaml`. The session name can be arbitrary.\n\n```yaml\napi_id: 1234567\napi_hash : some12321hashthatmustbehere123\nsession_name: somesessionyo\n```\n\nThis template file is provided with the repository.\n\n# Usage\n\n`tegracli` is a terminal application to access the Telegram API for research purposes.\nIn order to retrieve messages the configuration-file from the section before must be present in the directory you start `tegracli`.\nThe following commands are available:\n\n## GET\n\nTo _get_ messages from a number of channels, use this command.\n\n```\nUsage: tegracli get [OPTIONS] [CHANNELS]...\n\n  Get messages for the specified channels by either ID or username.\n\nOptions:\n  -l, --limit INTEGER           Number of messages to retrieve.\n  -O, --offset_date [%Y-%m-%d]  Offset retrieval to specific date in YYYY-MM-\n                                DD format.\n  -o, --offset_id INTEGER       Offset retrieval to a specific post number.\n  -m, --min_id INTEGER          Minimal post number.\n  -M, --max_id INTEGER          Maximal post number\n  -a, --add_offset INTEGER      Add an offset to the post numbers to be\n                                retrieved.\n  -f, --from_user TEXT          Only messages from this user.\n  --reverse / --forward         Should post numbers count upward or downward.\n                                Defaults to forward.\n  -r, --reply_to TEXT           Only messages replied to specific post id.\n  --help                        Show this message and exit.\n```\n| **parameter**       | **description**                                                                                                              |\n| ------------------- | ---------------------------------------------------------------------------------------------------------------------------- |\n| **channels**        | a list of of either telegram usernames, channel or group URLs or user IDs.                                                   |\n| **limit**           | number of messages to retrieve, positive integer. If set to `-1` , retrieves all messages in the channel. defaults to `-1`.  |\n| **offset_date**     | specify start point of retrieval by date, retrieval direction is controlled by `reverse/forward`. Format must be YYYY-MM-DD. |\n| **offset_id**       | specify start point of retrieval by post number, retrieval direction is controlled by `reverse/forward`.                     |\n| **min_id**          | sets the minimum post number                                                                                                 |\n| **max_id**          | sets the maximum post number                                                                                                 |\n| **add_offset**      | add a offset to the post numbers to be retrieved                                                                             |\n| **from_user**       | limit messages to posts *from* a specific user                                                                               |\n| **reply_to**        | limit messages to replies *to* a specific user                                                                               |\n| **reverse/forward** | flag to indicate whether messages should be retrieved in chronological or reverse chronological order.                       |\n\n### Basic Examples\n\nTo retrieve the last fifty messages from a Telegram channel:\n\n```\ntegracli get --limit 50 corona_infokanal_bmg\n```\n\nTo retrieve the entire history starting with post #1 of a channel, set `limit` to `-1`.\n\n```\ntegracli get --reverse --limit -1 corona_infokanal_bmg\n```\nTo retrieve messages sent after Januar, 1st 2022:\n\n```\ntegracli get --offset_data 2022-01-01 corona_infokanal_bmg\n```\n\nTo retrieve message sent before Januar, 1st 2022:\n\n```\ntegracli get --reverse --offset_data 2022-01-01 corona_infokanal_bmg\n```\n## SEARCH\n\nTo _search_ messages of your chats and groups and channels you are subscribed to, use this command.\n\n```\nUsage: tegracli search [OPTIONS] [QUERIES]...\n\n  This function searches Telegram content that is available to your account for the specified search term(s).\n\nOptions:\n  --help  Show this message and exit.\n```\n\n## Result File Format\n\nMessages are stored in `jsonl`-files per channel or query. For channels filename is the channel's or user's id, for searches the query.\n**BEWARE:** how directories and files are layed out is subject to active development and prone to changes in the near future.\n\n# Developer Installation\n\n1. Install [poetry](https://python-poetry.org/docs/#installation),\n2. Clone repository and unzip, if necessary,\n3. In the directory run `poetry install`,\n4. Run `poetry shell` to start the development virtualenv,\n6. Run `pytest` to run tests, run `pytest --run_api` too include tests against the Telegram API (**these do require a valid configuration**), coverage report can be found under `tests/coverage`.\n",
    'author': 'Philipp Kessling',
    'author_email': 'p.kessling@leibniz-hbi.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/tegracli/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
