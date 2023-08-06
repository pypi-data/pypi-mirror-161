# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['octue',
 'octue.cloud',
 'octue.cloud.deployment',
 'octue.cloud.deployment.google',
 'octue.cloud.deployment.google.cloud_run',
 'octue.cloud.deployment.google.dataflow',
 'octue.cloud.emulators',
 'octue.cloud.pub_sub',
 'octue.cloud.storage',
 'octue.essentials',
 'octue.migrations',
 'octue.mixins',
 'octue.resources',
 'octue.templates',
 'octue.templates.template-child-services.elevation_service',
 'octue.templates.template-child-services.parent_service',
 'octue.templates.template-child-services.wind_speed_service',
 'octue.templates.template-fractal',
 'octue.templates.template-fractal.fractal',
 'octue.templates.template-using-manifests',
 'octue.templates.template-using-manifests.cleaner',
 'octue.utils']

package_data = \
{'': ['*'],
 'octue.templates.template-child-services.parent_service': ['data/input/*'],
 'octue.templates.template-fractal': ['data/configuration/*'],
 'octue.templates.template-using-manifests': ['data/configuration/*',
                                              'data/input/*',
                                              'data/input/raw_met_mast_data/*',
                                              'data/input/raw_met_mast_data/08DEC/*']}

install_requires = \
['Flask==2.0.3',
 'click>=7,<9',
 'coolname>=1.1,<2.0',
 'google-auth>=1.27.0,<3',
 'google-cloud-pubsub>=2.5,<3.0',
 'google-cloud-secret-manager>=2.3,<3.0',
 'google-cloud-storage>=1.35.1,<3',
 'google-crc32c>=1.1,<2.0',
 'gunicorn>=20.1,<21.0',
 'packaging>=20.4,<22',
 'python-dateutil>=2.8,<3.0',
 'pyyaml>=6,<7',
 'twined>=0.5.0,<0.6.0']

extras_require = \
{'dataflow': ['apache-beam>=2.37,<3.0',
              'cachetools>=3.1.0,<5',
              'google-apitools>=0.5.31,<0.5.32',
              'google-auth-httplib2>=0.1.0,<0.2.0',
              'google-cloud-datastore>=1.8.0,<2'],
 'hdf5': ['h5py>=3.6,<4.0']}

entry_points = \
{'console_scripts': ['octue = octue.cli:octue_cli']}

setup_kwargs = {
    'name': 'octue',
    'version': '0.31.0',
    'description': 'A package providing template applications for data services, and a python SDK to the Octue API.',
    'long_description': '[![PyPI version](https://badge.fury.io/py/octue.svg)](https://badge.fury.io/py/octue)\n[![Release](https://github.com/octue/octue-sdk-python/actions/workflows/release.yml/badge.svg)](https://github.com/octue/octue-sdk-python/actions/workflows/release.yml)\n[![codecov](https://codecov.io/gh/octue/octue-sdk-python/branch/main/graph/badge.svg?token=4KdR7fmwcT)](https://codecov.io/gh/octue/octue-sdk-python)\n[![Documentation Status](https://readthedocs.org/projects/octue-python-sdk/badge/?version=latest)](https://octue-python-sdk.readthedocs.io/en/latest/?badge=latest)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n# Octue Python SDK <img src="./docs/source/images/213_purple-fruit-snake-transparent.gif" alt="Purple Fruit Snake" width="100"/></span>\n\nThe python SDK for running [Octue](https://octue.com) data services, digital twins, and applications - get faster data\ngroundwork so you have more time for the science!\n\nRead the docs [here.](https://octue-python-sdk.readthedocs.io/en/latest/)\n\nUses our [twined](https://twined.readthedocs.io/en/latest/) library for data validation.\n\n## Installation and usage\nTo install, run one of:\n```shell\npip install octue\n```\n\n```shell\npoetry add octue\n```\n\nThe command line interface (CLI) can then be accessed via:\n```shell\noctue --help\n```\n\n```text\nUsage: octue [OPTIONS] COMMAND [ARGS]...\n\n  The CLI for the Octue SDK. Use it to start an Octue data service or digital\n  twin locally or run an analysis on one locally.\n\n  Read more in the docs: https://octue-python-sdk.readthedocs.io/en/latest/\n\nOptions:\n  --id UUID                       UUID of the analysis being undertaken. None\n                                  (for local use) will cause a unique ID to be\n                                  generated.\n  --logger-uri TEXT               Stream logs to a websocket at the given URI.\n  --log-level [debug|info|warning|error]\n                                  Log level used for the analysis.  [default:\n                                  info]\n  --force-reset / --no-force-reset\n                                  Forces a reset of analysis cache and outputs\n                                  [For future use, currently not implemented]\n                                  [default: force-reset]\n  --version                       Show the version and exit.\n  -h, --help                      Show this message and exit.\n\nCommands:\n  deploy  Deploy a python app to the cloud as an Octue service or digital...\n  run     Run an analysis on the given input data using an Octue service...\n  start   Start an Octue service or digital twin locally as a child so it...\n```\n\n## Deprecated code\nWhen code is deprecated, it will still work but a deprecation warning will be issued with a suggestion on how to update\nit. After an adjustment period, deprecations will be removed from the codebase according to the [code removal schedule](https://github.com/octue/octue-sdk-python/issues/415).\nThis constitutes a breaking change.\n\n## Developer notes\n\n### Installation\nWe use [Poetry](https://python-poetry.org/) as our package manager. For development, run the following from the\nrepository root, which will editably install the package:\n\n```shell\npoetry install -E dataflow -E hdf5\n```\n\nThen run the tests to check everything\'s working.\n\n### Testing\nThese environment variables need to be set to run the tests:\n* `GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service/account/file.json`\n* `TEST_PROJECT_NAME=<name-of-google-cloud-project-to-run-pub-sub-tests-on>`\n\nThen, from the repository root, run\n```shell\npython3 -m unittest\n```\nor\n```shell\ntox\n```\n\n## Contributing\nTake a look at our [contributing](/docs/contributing.md) page.\n',
    'author': 'Marcus Lugg',
    'author_email': 'cortado.codes@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.github.com/octue/octue-sdk-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
