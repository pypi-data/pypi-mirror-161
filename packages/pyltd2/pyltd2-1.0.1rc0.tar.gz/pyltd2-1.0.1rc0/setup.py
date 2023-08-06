# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyltd2']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.16.5,<2.0.0',
 'pandas>=1.2.0,<2.0.0',
 'requests>=2.1.0,<3.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'pyltd2',
    'version': '1.0.1rc0',
    'description': 'Client package for the download of Legion TD 2 game data.',
    'long_description': '# pyltd2\n\nClient package for the download of Legion TD 2 game data. \n\n# Installation\n\n## Dependencies\n\n* numpy (>= 1.16.5)\n* pandas (>= 1.2.0)\n* tqdm (>= 4.64.0)\n* requests (>= 2.1.0)\n\n--- \n\n`pyltdq2` can be installed using pip with the following command:\n```\npip install pyltd2\n```\n\n# Data structure\nThe object stores the data into five separate objects, regarding separate information about each match:\n1. <details><summary>The fighters the player built during each wave and their position</summary>(_id, playerId, wave, fighter, x, y, seq_num)</details>\n2. <details><summary>The actions (Placed/Sold/Upgraded) the player made during each wave (alternative to the previous one, makes the file smaller but requires re-building the data)</summary>(_id, playerId, wave, fighter, x, y, action, seq_num)</details>\n3. <details><summary>The fighters the player had</summary>(_id, playerId, fighter_1, fighter_2, ..., fighter_30)</details>\n4. <details><summary>The king\'s hp at the end of the wave</summary>(_id, wave, left_hp, right_hp)</details>\n5. <details><summary>The king\'s upgrades bought by each player during each wave</summary>(_id, playerId, wave, upgrade, seq_num)</details>\n6. <details><summary>The leaks a player had during each wave</summary>(_id, playerId, wave, unit, seq_num)</details>\n7. <details><summary>The match itself</summary>(_id, version, date, queueType, endingWave, gameLength, gameElo, playerCount, humanCount, kingSpell, side_won)</details>\n8. <details><summary>The mercenaries the player received or sent during a wave</summary>(_id, playerId, received, wave, mercenary, seq_num)</details>\n9. <details><summary>The party members of each match</summary>(_id, member_1, member_2, member_3, member_4, member_5, member_6, member_7, member_8)</details>\n10. <details><summary>The players of the match</summary>(_id, playerId, playerName, playerSlot, legion, workers, value, cross, overallElo, stayedUntilEnd, chosenSpell, partySize, legionSpecificElo, mvpScore, leekValue, leaksCaughtValue, leftAtSeconds)</details>\n11. <details><summary>The player\'s economy during each wave</summary>(_id, playerId, wave, workers, income, networth)</details>\n12. <details><summary>The spell upgrades available in the match</summary>(_id, choice_1, choice_2, choice_3)</details>\n\n# Examples\nThe following example shows how to get the details of the next 50 matches, starting from the first match played (2018-08-03T15:39:00Z) and returning the data as a DataFrame object.\n```\nfrom pyltd2 import LTD2Fetcher\n\nfetcher = LTD2Fetcher("your_api_token")\nfetcher.get(return_as_df=True)\n```\nThe object uses the [getMatchesByFilter](https://swagger.legiontd2.com/#/Games/getMatchesByFilter) API command to fetch a maximum of 50 matches, starting from the date_after datetime provided.\n\nTo download data for the period of time between date_after-date_before and save them to a csv file, you can use the ExhaustiveFetcher object.\nThe following example downloads matches from 2018-08-03T15:39:00Z until 2019-12-25T22:03:40Z and saves the data to csv files inside the data folder.\n```\nfrom datetime import datetime\nfrom pyltd2 import LTD2Fetcher, ExhaustiveFetcher\n\nfetcher = LTD2Fetcher(\n    "your_api_token", \n    date_after=datetime(2018, 8, 3, 15, 39, 00), \n    date_before=datetime(2019, 12, 25, 22, 3, 40)\n)\napi2csv = ExhaustiveFetcher("./data", fetcher=fetcher)\napi2csv.start_fetching()\n```\n\nYou can get your own api token by registering [here](https://developer.legiontd2.com/home).\n',
    'author': 'GCidd',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/GCidd/pyltd2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
