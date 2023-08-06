# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hunt',
 'hunt.attributes',
 'hunt.attributes.xml',
 'hunt.cli',
 'hunt.cli.arguments',
 'hunt.database',
 'hunt.filesystem',
 'hunt.steam']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.5,<0.5.0', 'watchdog>=2.1.9,<3.0.0']

entry_points = \
{'console_scripts': ['hunt-match-telemetry-cli = hunt.cli.app:console_main']}

setup_kwargs = {
    'name': 'hunt-match-telemetry',
    'version': '1.6.3',
    'description': 'Automatically extract match data from Hunt: Showdown matches.',
    'long_description': '[![Run Tests CI](https://github.com/anthonyprintup/hunt-match-telemetry/actions/workflows/run-tests.yaml/badge.svg)](https://github.com/anthonyprintup/hunt-match-telemetry/actions/workflows/run-tests.yaml)\n\n# Hunt Match Telemetry\nThis tool is intended to be used for automatically logging match data provided by the game.\n\n# Installation\n- Create a new Python 3.10 [virtual environment](https://docs.python.org/3/library/venv.html) and activate it, <sup><sub>(optional)<sub/></sup>\n- run `pip install hunt-match-telemetry` to install the package,\n- download the [Steamworks SDK](https://partner.steamgames.com/downloads/steamworks_sdk.zip) and place it in `./resources/steam` as `steamworks_sdk.zip`.\n\n# Instructions\n- Run the CLI version of the package by executing `hunt-match-telemetry-cli` in your preferred terminal,\n- join a match from the game,\n- finish the game (extract, die, etc.),\n- return to the lobby screen (or any UI element that updates the last match information).\n\n# Screenshots\n<!--suppress CheckImageSize, HtmlDeprecatedAttribute -->\n<p align="center">\n    Console log:\n    <br/>\n    <img alt="Console Log" src="https://github.com/anthonyprintup/hunt-match-telemetry/blob/main/assets/console_log_example.png?raw=true" />\n</p>\n<p align="center">\n    Match log:\n    <br/>\n    <img alt="Match Log" src="https://github.com/anthonyprintup/hunt-match-telemetry/blob/main/assets/match_log_example.png?raw=true" />\n</p>\n<p align="center">\n    Player log:\n    <br/>\n    <img alt="Player Log" src="https://github.com/anthonyprintup/hunt-match-telemetry/blob/main/assets/player_log_example.png?raw=true" width="715"/>\n</p>\n\n# Notice of Non-Affiliation and Disclaimer\nWe are not affiliated, associated, authorized, endorsed by, or in any way officially connected with Crytek GmbH, or any of its subsidiaries or its affiliates.\n\nThe official Crytek GmbH website can be found at https://www.crytek.com/.\nThe official Hunt: Showdown website can be found at https://www.huntshowdown.com/.\n\nAll product and company names are the registered trademarks of their original owners. The use of any trade name or trademark is for identification and reference purposes only and does not imply any association with the trademark holder of their product brand.\n',
    'author': 'Anthony Printup',
    'author_email': 'anthony@printup.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/anthonyprintup/hunt-match-telemetry',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
