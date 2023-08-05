# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pylogformats', 'pylogformats.json', 'pylogformats.text']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pylogformats',
    'version': '1.0.0',
    'description': 'PyLogFormats',
    'long_description': '# PyLogFormats\n\n[![PyPI](https://img.shields.io/pypi/v/pylogformats.svg)][pypi_]\n[![Status](https://img.shields.io/pypi/status/pylogformats.svg)][status]\n[![Python Version](https://img.shields.io/pypi/pyversions/pylogformats)][python version]\n[![License](https://img.shields.io/pypi/l/pylogformats)][license]\n\n[![Read the documentation at https://pylogformats.readthedocs.io/](https://img.shields.io/readthedocs/pylogformats/latest.svg?label=Read%20the%20Docs)][read the docs]\n[![Tests](https://github.com/MattLimb/pylogformats/workflows/Tests/badge.svg)][tests]\n[![Codecov](https://codecov.io/gh/MattLimb/pylogformats/branch/main/graph/badge.svg)][codecov]\n\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]\n\n[pypi_]: https://pypi.org/project/pylogformats/\n[status]: https://pypi.org/project/pylogformats/\n[python version]: https://pypi.org/project/pylogformats\n[read the docs]: https://pylogformats.readthedocs.io/\n[tests]: https://github.com/MattLimb/pylogformats/actions?workflow=Tests\n[codecov]: https://app.codecov.io/gh/MattLimb/pylogformats\n[pre-commit]: https://github.com/pre-commit/pre-commit\n[black]: https://github.com/psf/black\n\n## Features\n\n- Json Formatters\n  - AdvJsonFormat\n  ```json\n  {\n    "logger": "root",\n    "timestamp": "2021-02-04T23:02:52.522958",\n    "rtimestamp": "2021-02-04T23:02:37.518800",\n    "message": "TEST",\n    "level": "ERROR",\n    "levelno": 40,\n    "location": {\n      "pathname": "<FULL_PATH>\\\\test_logger.py",\n      "module": "test_logger",\n      "filename": "test_logger.py",\n      "function": "<module>",\n      "line": 16\n    },\n    "process": {\n      "number": 2300,\n      "name": "MainProcess"\n    },\n    "thread": {\n      "number": 12516,\n      "name": "MainThread"\n    },\n    "v": 1\n  }\n  ```\n  - BunyanFormat\n  ```json\n  {\n    "time": "2021-02-04T23:01:00.781Z",\n    "name": "root",\n    "pid": 15504,\n    "level": 40,\n    "msg": "TEST",\n    "hostname": "HerculesPC",\n    "v": 0\n  }\n  ```\n  - JsonFormat\n  ```json\n  {\n    "logger": "root",\n    "timestamp": "2021-02-04T23:01:46.435011",\n    "message": "TEST",\n    "level": "ERROR",\n    "levelno": 40,\n    "function": "<module>",\n    "process": {\n      "number": 13316,\n      "name": "MainProcess"\n    },\n    "thread": {\n      "number": 10704,\n      "name": "MainThread"\n    },\n    "v": 1\n  }\n  ```\n- Text Formatters\n\n  - SimpleTextFormat\n\n  ```text\n  [DEBUG] [2021-02-04 23:01:46] A Test Debug Log\n  ```\n\n  - CompactTextFormat\n\n  ```text\n  [D 2021-02-04 23:01:46 l:root f:<module> ln:5] A Test Log [includesExtras:Yes]\n  ```\n\n## Installation\n\nYou can install _PyLogFormats_ via [pip] from [PyPI]:\n\n```console\n$ pip install pylogformats\n```\n\n## Usage\n\nFor an explanation of this, and more usage instructions please visit the [documentation](https://pylogformats.readthedocs.io/usage.html)\n\n```py\nimport logging\nimport sys\n\nfrom pylogformats import JsonFormat\n\n# Create the logging handler\nhandler = logging.StreamHandler(sys.stdout)\n\n# Add the formatter class to the handler we just created.\nhandler.setFormatter(JsonFormat())\n\n# Use basicConfig to setup the loggers.\nlogging.basicConfig(handlers=[handler], level=logging.DEBUG)\n\n# Use the normal logging methods to see formatted logs in your terminal\nlogging.critical("Critical Log")\nlogging.error("Error Log")\nlogging.warning("Warning Log")\nlogging.info("Info Log")\nlogging.debug("Debug Log")\n\n```\n\n## Contributing\n\nContributions are very welcome.\nTo learn more, see the [Contributor Guide].\n\n## License\n\nDistributed under the terms of the [MIT license][license],\n_PyLogFormats_ is free and open source software.\n\n## Issues\n\nIf you encounter any problems,\nplease [file an issue] along with a detailed description.\n\n## Credits\n\nThis project was generated from [@cjolowicz]\'s [Hypermodern Python Cookiecutter] template.\n\n[@cjolowicz]: https://github.com/cjolowicz\n[pypi]: https://pypi.org/\n[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n[file an issue]: https://github.com/MattLimb/pylogformats/issues\n[pip]: https://pip.pypa.io/\n\n<!-- github-only -->\n\n[license]: https://github.com/MattLimb/pylogformats/blob/main/LICENSE\n[contributor guide]: https://github.com/MattLimb/pylogformats/blob/main/CONTRIBUTING.md\n',
    'author': 'Matt Limb',
    'author_email': 'matt.limb17@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MattLimb/pylogformats',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
