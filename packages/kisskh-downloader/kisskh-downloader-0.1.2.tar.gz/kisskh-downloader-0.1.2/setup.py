# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['kisskh_downloader', 'kisskh_downloader.enums', 'kisskh_downloader.models']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'requests>=2.28.1,<3.0.0',
 'validators>=0.20.0,<0.21.0',
 'yt-dlp>=2022.7.18,<2023.0.0']

entry_points = \
{'console_scripts': ['kisskh = kisskh_downloader.cli:kisskh']}

setup_kwargs = {
    'name': 'kisskh-downloader',
    'version': '0.1.2',
    'description': 'Simple downloaded for https://kisskh.me/',
    'long_description': '# :tv: kisskh-dl\n\nSimple downloaded for https://kisskh.me/\n\n---\n\n## :inbox_tray: Installation\n\n```console\npip install kisskh-downloader\n```\n\n## :books: Usage\n\n```console\ndl [OPTIONS] DRAMA_URL_OR_NAME\n\nOptions:\n  -f, --first INTEGER             Starting episode number.\n  -l, --last INTEGER              Ending episode number.\n  -q, --quality [360p|480p|540p|720p|1080p]\n                                  Quality of the video to be downloaded.\n  -s, --sub-langs TEXT            Languages of the subtitles to download.\n  -o, --output-dir TEXT           Output directory where downloaded files will\n                                  be store.\n  --help                          Show this message and exit.\n```\n\n### :high_brightness: Direct download entire series in highest quality available\n\n```console\nkisskh dl "https://kisskh.me/Drama/Money-Heist--Korea---Joint-Economic-Area?id=5044"\n```\n\n### :mag_right: Search and download entire series in highest quality available\n\n```console\nkisskh dl "Stranger Things"\n1. Stranger Things - Season 4\n2. Stranger Things - Season 1\n3. Stranger Things - Season 2\n4. Stranger Things - Season 3\nPlease select one from above: 1\n```\n\n### :arrow_forward: Download specific episodes with specific quality\n\n> :exclamation: Note that if the selected quality is not available, it will try to get something lower than that quality. If that also is not available, it will try to get the best quality available.\n\nDownloads episode 4 to 8 of `Alchemy of Souls` in 720p:\n```console\nkisskh dl "https://kisskh.me/Drama/Alchemy-of-Souls?id=5043" -f 4 -l 8 -q 720p\n```\n\nDownloads episode 3 of `A Business Proposal` in 720p:\n```console\nkisskh dl "https://kisskh.me/Drama/A-Business-Proposal?id=4608" -f 3 -l 3 -q 720p\n```\n\n---\n\n# :construction: TODO\n- [ ] Add unit test\n- [ ] Enable CI/CD for linting (flake8), formatting (black and isort) and security (bandit)\n- [ ] Add ability to export all download link\n- [ ] Add ability to open stream in some player',
    'author': 'Debakar Roy',
    'author_email': 'allinonedibakar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
