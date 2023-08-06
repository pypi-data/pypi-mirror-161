# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tft_loaded_dice']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tft-loaded-dice',
    'version': '12.14.0',
    'description': 'Loaded dice odds for Teamfight Tactics',
    'long_description': '## tft-loaded-dice\n[![Pypi](https://img.shields.io/pypi/v/tft-loaded-dice)](https://pypi.org/project/tft-loaded-dice/)\n[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/stradivari96/tft-loaded-dice/blob/master/LICENSE)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n<a href="https://gitmoji.dev">\n  <img src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg" alt="Gitmoji">\n</a>\n\n![loaded dice](https://static.wikia.nocookie.net/leagueoflegends/images/b/b7/Twisted_Fate_Loaded_Dice.png)\n## Usage\nUse the resulting [json](https://raw.githubusercontent.com/stradivari96/tft-loaded-dice/main/tft_loaded_dice/data.json)\n\nor\n```\npip install tft-loaded-dice\n```\n```python\nfrom tft_loaded_dice import best_champions, champion_odds\n\nbest_champions("Jayce", level=7)\n# [(\'Zilean\', 0.01), (\'Jayce\', 0.01), (\'Caitlyn\', 0.01), (\'Fiora\', 0.005), (\'Singed\', 0.005), (\'Ezreal\', 0.005), (\'Heimerdinger\', 0.005), (\'Seraphine\', 0.005), (\'Vi\', 0.003333333333333333)]\n\nchampion_odds("Shaco")\n# {\'Ekko\': {3: 0.0, 4: 0.075, 5: 0.1, 6: 0.15, 7: 0.175, 8: 0.175, 9: 0.15, 10: 0.1, 11: 0.06}, \'Braum\': {3: 0.0, 4: 0.075, 5: 0.1, 6: 0.15, 7: 0.175, 8: 0.175, 9: 0.15, 10: 0.1, 11: 0.06}, \'Talon\': {3: 0.0, 4: 0.05, 5: 0.06666666666666667, 6: 0.1, 7: 0.11666666666666665, 8: 0.11666666666666665, 9: 0.1, 10: 0.06666666666666667, 11: 0.04}, \'Shaco\': {3: 0.0, 4: 0.075, 5: 0.1, 6: 0.15, 7: 0.175, 8: 0.175, 9: 0.15, 10: 0.1, 11: 0.06}, \'Twisted Fate\': {3: 0.0, 4: 0.05, 5: 0.06666666666666667, 6: 0.1, 7: 0.11666666666666665, 8: 0.11666666666666665, 9: 0.1, 10: 0.06666666666666667, 11: 0.04}, \'Twitch\': {3: 0.0, 4: 0.0375, 5: 0.05, 6: 0.075, 7: 0.0875, 8: 0.0875, 9: 0.075, 10: 0.05, 11: 0.03}, \'Darius\': {3: 0.0, 4: 0.075, 5: 0.1, 6: 0.15, 7: 0.175, 8: 0.175, 9: 0.15, 10: 0.1, 11: 0.06}, \'Akali\': {3: 0.0, 4: 0.075, 5: 0.1, 6: 0.15, 7: 0.175, 8: 0.175, 9: 0.15, 10: 0.1, 11: 0.06}, \'Katarina\': {3: 0.0, 4: 0.05, 5: 0.06666666666666667, 6: 0.1, 7: 0.11666666666666665, 8: 0.11666666666666665, 9: 0.1, 10: 0.06666666666666667, 11: 0.04}, \'Zyra\': {3: 0.0, 4: 0.05, 5: 0.06666666666666667, 6: 0.1, 7: 0.11666666666666665, 8: 0.11666666666666665, 9: 0.1, 10: 0.06666666666666667, 11: 0.04}}\n```\n\n## Development\n\n1. Install poetry\n\nhttps://python-poetry.org/docs/#installation\n\n2. Install dependencies\n```\npoetry install\npoetry run pre-commit install\n```\n\n3. Run test\n```\npoetry run pytest --cov=tft_loaded_dice --cov-fail-under=80 --cov-report xml\n```\n\n## References\n* https://github.com/alanz132/loadedDiceOdds\n* https://giantslayer.tv/blogs/5261054387/correctly-using-loaded-dice/\n* https://www.reddit.com/r/CompetitiveTFT/comments/kw4ah7/loaded_die_odds_for_every_champion/\n* https://raw.communitydragon.org/latest/cdragon/tft/en_gb.json\n',
    'author': 'Xiang Chen',
    'author_email': 'xiangchenchen96@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/stradivari96/tft-loaded-dice',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
