# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cert_host_scraper']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp[speedups]>=3.8.1,<4.0.0',
 'beautifulsoup4>=4.10.0,<5.0.0',
 'click>=8.0.3,<9.0.0',
 'requests>=2.27.1,<3.0.0',
 'rich>=11.0.0,<12.0.0']

entry_points = \
{'console_scripts': ['cert-host-scraper = cert_host_scraper.cli:cli']}

setup_kwargs = {
    'name': 'cert-host-scraper',
    'version': '0.2.0',
    'description': '',
    'long_description': '# Cert Host Scraper\n\n![CI](https://github.com/inverse/cert-host-scraper/workflows/CI/badge.svg)\n[![PyPI version](https://badge.fury.io/py/cert-host-scraper.svg)](https://badge.fury.io/py/cert-host-scraper)\n![PyPI downloads](https://img.shields.io/pypi/dm/cert-host-scraper?label=pypi%20downloads)\n[![License](https://img.shields.io/github/license/inverse/cert-host-scraper.svg)](LICENSE)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nQuery the certificate transparency log for a keyword and check the status code of the results. Optionally filtering out based on the code.\n\n## Usage\n\n```bash\ncert-host-scraper search your-domain.com [--status-code 200]\n```\n\n## Installation\n\nWith pipx:\n\n```bash\npipx install cert-host-scraper\n```\n\nWith pip:\n\n```bash\npip install cert-host-scraper\n```\n\n## Licence\n\nMIT\n',
    'author': 'Malachi Soord',
    'author_email': 'inverse.chi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/inverse/cert-host-scraper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
