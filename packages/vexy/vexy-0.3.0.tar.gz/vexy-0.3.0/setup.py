# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vexy', 'vexy.parser', 'vexy.sources']

package_data = \
{'': ['*']}

install_requires = \
['cyclonedx-python-lib>=3.0.0rc1,<4.0.0',
 'ossindex-lib>=1.1.0,<2.0.0',
 'osv-lib>=0.2.1,<0.3.0',
 'packageurl-python>=0.9',
 'rich>=12.4.4,<13.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=3.4']}

entry_points = \
{'console_scripts': ['vexy = vexy.client:main']}

setup_kwargs = {
    'name': 'vexy',
    'version': '0.3.0',
    'description': 'Generate VEX (Vulnerability Exploitability Exchange) CycloneDX documents',
    'long_description': '# Vexy - Generate VEX in CycloneDX\n\n[![shield_gh-workflow-test]][link_gh-workflow-test]\n[![shield_rtfd]][link_rtfd]\n[![shield_pypi-version]][link_pypi]\n[![shield_docker-version]][link_docker]\n[![shield_license]][license_file]\n[![shield_twitter-follow]][link_twitter]\n\n----\n\nThis project provides a runnable Python-based application for generating VEX (Vulnerability Exploitability Exchange) in\nCycloneDX format.\n\nThis tool is intended to be supplied a [CycloneDX](https://cyclonedx.org/) SBOM file and will produce a separate VEX\nwhich contains known vulnerabilities from a selection of publicly available data sources.\n\n[CycloneDX](https://cyclonedx.org/) is a lightweight BOM specification that is easily created, human-readable, and simple to parse.\n\nRead the full [documentation][link_rtfd] for more details.\n\n## Why?\n\nA SBOM (Software Bill of Materials) is great for cataloging / knowing what components compose a software product.\n\nThe same SBOM (in CycloneDX format) can also note _known_ vulnerabilities. What is _known_ is for a given point \nin time - and will change as new vulnerabilities are discovered or disclosed.\n\nCycloneDX allows for separate BOM documents to reference each other through their \n[BOM Link](https://cyclonedx.org/capabilities/bomlink/) capability.\n\nWouldn\'t it be great if you could periodically generate a VEX based from your SBOM to keep things up to date, \nwithout having to generate a fresh SBOM entirely?\n\nThat is where **vexy** comes in.\n\n## Installation\n\nInstall this from [PyPi.org][link_pypi] using your preferred Python package manager.\n\nExample using `pip`:\n\n```shell\npip install vexy\n```\n\nExample using `poetry`:\n\n```shell\npoetry add vexy\n```\n\n## Usage\n\n## Basic usage\n\n```text\n$ vexy --help\n\nusage: vexy [-h] -i FILE_PATH [--format {xml,json}] [--schema-version {1.4}] [-o FILE_PATH] [--force] [-X]\n\nVexy VEX Generator\n\noptions:\n  -h, --help            show this help message and exit\n  -X                    Enable debug output\n\nInput CycloneDX BOM:\n  Where Vexy shall obtain it\'s input\n\n  -i FILE_PATH, --in-file FILE_PATH\n                        CycloneDX BOM to read input from. Use "-" to read from STDIN.\n\nVEX Output Configuration:\n  Choose the output format and schema version\n\n  --format {xml,json}   The output format for your SBOM (default: xml)\n  --schema-version {1.4}\n                        The CycloneDX schema version for your VEX (default: 1.4)\n  -o FILE_PATH, --o FILE_PATH, --output FILE_PATH\n                        Output file path for your SBOM (set to \'-\' to output to STDOUT)\n  --force               If outputting to a file and the stated file already exists, it will be overwritten.\n\n```\n\n### Advanced usage and details\n\nSee the full [documentation][link_rtfd] for advanced usage and details on input formats, switches and options.\n\n## Python Support\n\nWe endeavour to support all functionality for all [current actively supported Python versions](https://www.python.org/downloads/).\nHowever, some features may not be possible/present in older Python versions due to their lack of support.\n\n## Contributing\n\nFeel free to open issues, bugreports or pull requests.  \nSee the [CONTRIBUTING][contributing_file] file for details.\n\n## Copyright & License\n\nVexy is Copyright (c) Paul Horton. All Rights Reserved.  \nPermission to modify and redistribute is granted under the terms of the Apache 2.0 license.  \nSee the [LICENSE][license_file] file for the full license.\n\n[license_file]: https://github.com/madpah/vexy/blob/master/LICENSE\n[contributing_file]: https://github.com/madpah/vexy/blob/master/CONTRIBUTING.md\n[link_rtfd]: https://vexy.readthedocs.io/\n\n[shield_gh-workflow-test]: https://img.shields.io/github/workflow/status/madpah/vexy/Python%20CI/master?logo=GitHub&logoColor=white "build"\n[shield_rtfd]: https://img.shields.io/readthedocs/vexy?logo=readthedocs&logoColor=white\n[shield_pypi-version]: https://img.shields.io/pypi/v/vexy?logo=Python&logoColor=white&label=PyPI "PyPI"\n[shield_docker-version]: https://img.shields.io/docker/v/madpah/vexy?logo=docker&logoColor=white&label=docker "docker"\n[shield_license]: https://img.shields.io/github/license/madpah/vexy?logo=open%20source%20initiative&logoColor=white "license"\n[shield_twitter-follow]: https://img.shields.io/badge/Twitter-follow-blue?logo=Twitter&logoColor=white "twitter follow"\n[link_gh-workflow-test]: https://github.com/madpah/vexy/actions/workflows/python.yml?query=branch%3Amaster\n[link_pypi]: https://pypi.org/project/vexy/\n[link_docker]: https://hub.docker.com/r/madpah/vexy\n[link_twitter]: https://twitter.com/madpah\n',
    'author': 'Paul Horton',
    'author_email': 'paul.horton@owasp.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/madpah/vexy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
