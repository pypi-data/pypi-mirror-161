# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['musicxml2fmf']
install_requires = \
['black>=22.6.0,<23.0.0', 'click>=8.1.3,<9.0.0', 'lxml>=4.9.1,<5.0.0']

entry_points = \
{'console_scripts': ['musicxml2fmf = musicxml2fmf:convert']}

setup_kwargs = {
    'name': 'musicxml2fmf',
    'version': '0.2.0',
    'description': 'MusicXML to Flipper Music Format',
    'long_description': '# MusicXML to Flipper Music Format\n\nThis script reads a (not compressed) [MusicXML](https://www.w3.org/2021/06/musicxml40/) ([Wikipedia](https://en.wikipedia.org/wiki/MusicXML)) file and transforms it to the [Flipper Music Format](https://github.com/Tonsil/flipper-music-files) which can be executed on the [Flipper Zero](https://flipperzero.one/).\n\nThis allows to compose your music with graphical tools like [MuseScore](https://en.wikipedia.org/wiki/MuseScore) and play the music on the Flipper.\n\n## Installation\n\nTo install the script you need [poetry](https://python-poetry.org/).\n\nRun:\n\n```\n$ poetry install\n…\n$ poetry run musicxml2fmf --help\n```\n\n## TODO\n\n### Ties\n\n```\n<notations>\n <tied type="stop"/>\n <tied type="start"/>\n</notations>\n```\n',
    'author': 'Natanael Arndt',
    'author_email': 'arndtn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/white-gecko/musicxml2fmf',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
