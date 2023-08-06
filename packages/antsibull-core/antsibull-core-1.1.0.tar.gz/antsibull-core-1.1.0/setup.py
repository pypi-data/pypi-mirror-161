# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['antsibull_core',
 'antsibull_core.schemas',
 'antsibull_core.utils',
 'antsibull_core.vendored',
 'tests',
 'tests.functional',
 'tests.units']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML',
 'aiofiles',
 'aiohttp>=3.0.0',
 'packaging>=20.0',
 'perky',
 'pydantic',
 'semantic_version',
 'sh',
 'twiggy>=0.5.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata'],
 ':python_version >= "3.6" and python_version < "3.7"': ['aiocontextvars']}

setup_kwargs = {
    'name': 'antsibull-core',
    'version': '1.1.0',
    'description': 'Tools for building the Ansible Distribution',
    'long_description': '<!--\nCopyright (c) Ansible Project\nGNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)\nSPDX-License-Identifier: GPL-3.0-or-later\n-->\n\n# antsibull-core -- Library for Ansible Build Scripts\n[![Python linting badge](https://github.com/ansible-community/antsibull-core/workflows/Python%20linting/badge.svg?event=push&branch=main)](https://github.com/ansible-community/antsibull-core/actions?query=workflow%3A%22Python+linting%22+branch%3Amain)\n[![Python testing badge](https://github.com/ansible-community/antsibull-core/workflows/Python%20testing/badge.svg?event=push&branch=main)](https://github.com/ansible-community/antsibull-core/actions?query=workflow%3A%22Python+testing%22+branch%3Amain)\n[![Codecov badge](https://img.shields.io/codecov/c/github/ansible-community/antsibull-core)](https://codecov.io/gh/ansible-community/antsibull-core)\n\nLibrary needed for tooling for building various things related to Ansible.\n\nYou can find a list of changes in [the antsibull-core changelog](./CHANGELOG.rst).\n\nUnless otherwise noted in the code, it is licensed under the terms of the GNU\nGeneral Public License v3 or, at your option, later.\n\nantsibull-core is covered by the [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html).\n\n## Versioning and compatibility\n\nFrom version 1.0.0 on, antsibull-core sticks to semantic versioning and aims at providing no backwards compatibility breaking changes during a major release cycle. We might make exceptions from this in case of security fixes for vulnerabilities that are severe enough.\n\n## Creating a new release:\n\nIf you want to create a new release::\n\n    vim pyproject.toml  # Make sure version number is correct\n    vim changelogs/fragment/$VERSION_NUMBER.yml  # create \'release_summary:\' fragment\n    antsibull-changelog release --version $VERSION_NUMBER\n    git add CHANGELOG.rst changelogs\n    git commit -m "Release $VERSION_NUMBER."\n    poetry build\n    poetry publish  # Uploads to pypi.  Be sure you really want to do this\n\n    git tag $VERSION_NUMBER\n    git push --tags\n    vim pyproject.toml  # Bump the version number to X.Y.Z.post0\n    git commit -m \'Update the version number for the next release\' pyproject.toml\n    git push\n\n## License\n\nUnless otherwise noted in the code, it is licensed under the terms of the GNU\nGeneral Public License v3 or, at your option, later. See\n[LICENSES/GPL-3.0-or-later.txt](https://github.com/ansible-community/antsibull-changelog/tree/main/LICENSE)\nfor a copy of the license.\n\nParts of the code are vendored from other sources and are licensed under other licenses:\n1. `src/antsibull_core/vendored/collections.py` and `src/antsibull_core/vendored/json_utils.py` are licensed under the terms of the BSD 2-Clause license. See [LICENSES/BSD-2-Clause.txt](https://github.com/ansible-community/antsibull-changelog/tree/main/LICENSES/BSD-2-Clause.txt) for a copy of the license.\n2. `tests/functional/aiohttp_utils.py` and `tests/functional/certificate_utils.py` are licensed under the terms of the MIT license. See [LICENSES/MIT.txt](https://github.com/ansible-community/antsibull-changelog/tree/main/LICENSES/MIT.txt) for a copy of the license.\n3. `src/antsibull_core/vendored/_argparse_booleanoptionalaction.py` is licensed under the terms of the Python Software Foundation license version 2. See [LICENSES/PSF-2.0.txt](https://github.com/ansible-community/antsibull-changelog/tree/main/LICENSES/PSF-2.0.txt) for a copy of the license.\n\nThe repository follows the [REUSE Specification](https://reuse.software/spec/) for declaring copyright and\nlicensing information. The only exception are changelog fragments in ``changelog/fragments/``.\n',
    'author': 'Toshio Kuratomi',
    'author_email': 'a.badger@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ansible-community/antsibull-core',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
