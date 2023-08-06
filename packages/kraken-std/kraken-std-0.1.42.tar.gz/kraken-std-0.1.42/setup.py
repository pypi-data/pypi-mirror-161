# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['std',
 'std.cargo',
 'std.cargo.tasks',
 'std.docker',
 'std.generic',
 'std.git',
 'std.git.tasks',
 'std.helm',
 'std.python',
 'std.python.buildsystem',
 'std.python.tasks']

package_data = \
{'': ['*'], 'std.cargo': ['data/certs/*']}

install_requires = \
['httpx>=0.23.0,<0.24.0',
 'kraken-core>=0.6.2,<0.7.0',
 'nr.python.environment>=0.1.4,<0.2.0',
 'proxy.py>=2.4.3,<3.0.0',
 'tomli-w>=1.0.0,<2.0.0',
 'tomli>=2.0.1,<3.0.0',
 'twine>=4.0.1,<5.0.0']

setup_kwargs = {
    'name': 'kraken-std',
    'version': '0.1.42',
    'description': 'The Kraken standard library.',
    'long_description': '# kraken-std\n\n[![Python application](https://github.com/kraken-build/kraken-std/actions/workflows/python-package.yml/badge.svg)](https://github.com/kraken-build/kraken-std/actions/workflows/python-package.yml)\n[![PyPI version](https://badge.fury.io/py/kraken-std.svg)](https://badge.fury.io/py/kraken-std)\n\nThe Kraken standard library.\n\n---\n\n## Development\n\n### Integration testing\n\nIntegration tests are located in `src/tests/integration`. The following tools need to be available to run the\nintegration tests:\n\n* Cargo (to test Cargo building and publishing) *The Cargo integration tests run against Artifactory and Cloudsmith\nand requires credentials to temporarily create a new Cargo repository (available in CI).*\n* Docker (used to setup services that we run integration tests against)\n* Helm (to test Helm packaging and publishing)\n* Poetry (to test Python publishing and installing)\n* [Slap](https://github.com/python-slap/slap-cli) (to test Python publishing and installing)\n\n__Test a single integration test__\n\n    ```\n    PYTEST_FLAGS="--log-cli-level DEBUG -s -k <test_filter>" kraken run pytestIntegration -v\n    ```\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
