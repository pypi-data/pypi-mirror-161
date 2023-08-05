# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['symphony',
 'symphony.bdk',
 'symphony.bdk.core',
 'symphony.bdk.core.activity',
 'symphony.bdk.core.activity.parsing',
 'symphony.bdk.core.auth',
 'symphony.bdk.core.client',
 'symphony.bdk.core.config',
 'symphony.bdk.core.config.model',
 'symphony.bdk.core.retry',
 'symphony.bdk.core.service',
 'symphony.bdk.core.service.application',
 'symphony.bdk.core.service.connection',
 'symphony.bdk.core.service.connection.model',
 'symphony.bdk.core.service.datafeed',
 'symphony.bdk.core.service.health',
 'symphony.bdk.core.service.message',
 'symphony.bdk.core.service.presence',
 'symphony.bdk.core.service.session',
 'symphony.bdk.core.service.signal',
 'symphony.bdk.core.service.stream',
 'symphony.bdk.core.service.user',
 'symphony.bdk.core.service.user.model',
 'symphony.bdk.ext',
 'symphony.bdk.gen',
 'symphony.bdk.gen.agent_api',
 'symphony.bdk.gen.agent_model',
 'symphony.bdk.gen.auth_api',
 'symphony.bdk.gen.auth_model',
 'symphony.bdk.gen.group_api',
 'symphony.bdk.gen.group_model',
 'symphony.bdk.gen.login_api',
 'symphony.bdk.gen.login_model',
 'symphony.bdk.gen.pod_api',
 'symphony.bdk.gen.pod_model']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.3.0,<3.0.0',
 'aiohttp>=3.8.1,<4.0.0',
 'cryptography>=36.0.0,<37.0.0',
 'defusedxml>=0.7.1,<0.8.0',
 'docutils==0.16',
 'nulltype>=2.3.1,<3.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'pyyaml>=6.0,<7.0',
 'tenacity>=8.0.1,<9.0.0',
 'urllib3>=1.26.9,<2.0.0']

setup_kwargs = {
    'name': 'symphony-bdk-python',
    'version': '2.4.1',
    'description': 'Symphony Bot Development Kit for Python',
    'long_description': "[![FINOS - Incubating](https://cdn.jsdelivr.net/gh/finos/contrib-toolbox@master/images/badge-incubating.svg)](https://finosfoundation.atlassian.net/wiki/display/FINOS/Incubating)\n[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9-blue)](https://www.python.org/downloads/release/python-3)\n[![Pypi](https://img.shields.io/pypi/v/symphony-bdk-python)](https://pypi.org/project/symphony-bdk-python/)\n![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/finos/symphony-bdk-python/build/main)\n\n# Symphony BDK for Python\n\nThis is the Symphony BDK for Python to help develop bots and interact with the [Symphony REST APIs](https://developers.symphony.com/restapi/reference).\n\n## Installation and getting started\nThe [reference documentation](https://symphony-bdk-python.finos.org/) includes detailed\ninstallation instructions as well as a comprehensive\n[getting started](https://symphony-bdk-python.finos.org/markdown/getting_started.html)\nguide.\n\n## Build from source\n\nThe Symphony BDK uses and requires Python 3.8 or higher. Be sure you have it installed before going further.\n\nWe use [poetry](https://python-poetry.org/) in order to manage dependencies, build, run tests and publish.\nTo install poetry, follow instructions [here](https://python-poetry.org/docs/#installation).\n\nOn the first time, run `poetry install`. Then run `poetry build` to build the sdist and wheel packages.\nTo run the tests, use `poetry run pytest`.\n\nIt is possible to run pylint scan locally (on a specific file or package) executing the following command:\n`poetry run pylint <module_name>`.\n\nTo generate locally the Sphinx documentation, run: `cd docsrc && make html`.\n\n## Roadmap\n\nOur next milestone is the [2.0.x](https://github.com/finos/symphony-bdk-python/milestone/1) one.\nIt will only consist in delivering the next improvements of the BDK.\n\n\n## Contributing\nIn order to get in touch with the project team, please open a [GitHub Issue](https://github.com/finos/symphony-bdk-python/issues).\nAlternatively, you can email/subscribe to [symphony@finos.org](https://groups.google.com/a/finos.org/g/symphony).\n\n1. Fork it\n2. Create your feature branch (`git checkout -b feature/fooBar`)\n3. Read our [contribution guidelines](CONTRIBUTING.md) and [Community Code of Conduct](https://www.finos.org/code-of-conduct)\n4. Commit your changes (`git commit -am 'Add some fooBar'`)\n5. Push to the branch (`git push origin feature/fooBar`)\n6. Create a new Pull Request\n\n_NOTE:_ Commits and pull requests to FINOS repositories will only be accepted from those contributors with an active,\nexecuted Individual Contributor License Agreement (ICLA) with FINOS OR who are covered under an existing and active\nCorporate Contribution License Agreement (CCLA) executed with FINOS.\nCommits from individuals not covered under an ICLA or CCLA will be flagged and blocked by the FINOS Clabot tool.\nPlease note that some CCLAs require individuals/employees to be explicitly named on the CCLA.\n\n*Need an ICLA? Unsure if you are covered under an existing CCLA? Email [help@finos.org](mailto:help@finos.org)*\n\n## License\nCopyright 2021 Symphony LLC\n\nDistributed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).\n\nSPDX-License-Identifier: [Apache-2.0](https://spdx.org/licenses/Apache-2.0)",
    'author': 'Symphony Platform Solutions',
    'author_email': 'symphony@finos.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/finos/symphony-bdk-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
