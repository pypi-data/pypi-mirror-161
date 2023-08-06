# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['antsibull_docs',
 'antsibull_docs.cli',
 'antsibull_docs.cli.doc_commands',
 'antsibull_docs.data',
 'antsibull_docs.data.docsite',
 'antsibull_docs.docs_parsing',
 'antsibull_docs.jinja2',
 'antsibull_docs.schemas',
 'antsibull_docs.schemas.docs',
 'antsibull_docs.utils',
 'sphinx_antsibull_ext',
 'tests',
 'tests.functional',
 'tests.functional.schema',
 'tests.units']

package_data = \
{'': ['*'],
 'antsibull_docs.data': ['sphinx_init/*'],
 'antsibull_docs.data.docsite': ['macros/*'],
 'sphinx_antsibull_ext': ['css/*'],
 'tests.functional.schema': ['good_data/*']}

install_requires = \
['ansible-pygments',
 'antsibull-core>=1.0.0,<2.0.0',
 'asyncio-pool',
 'docutils',
 'jinja2',
 'rstcheck>=3.0.0,<7.0.0',
 'sphinx']

entry_points = \
{'console_scripts': ['antsibull-docs = antsibull_docs.cli.antsibull_docs:main']}

setup_kwargs = {
    'name': 'antsibull-docs',
    'version': '1.2.0',
    'description': 'Tools for building Ansible documentation',
    'long_description': '<!--\nCopyright (c) Ansible Project\nGNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)\nSPDX-License-Identifier: GPL-3.0-or-later\n-->\n\n# antsibull-docs -- Ansible Documentation Build Scripts\n[![Python linting badge](https://github.com/ansible-community/antsibull-docs/workflows/Python%20linting/badge.svg?event=push&branch=main)](https://github.com/ansible-community/antsibull-docs/actions?query=workflow%3A%22Python+linting%22+branch%3Amain)\n[![Python testing badge](https://github.com/ansible-community/antsibull-docs/workflows/Python%20testing/badge.svg?event=push&branch=main)](https://github.com/ansible-community/antsibull-docs/actions?query=workflow%3A%22Python+testing%22+branch%3Amain)\n[![Build docs testing badge](https://github.com/ansible-community/antsibull-docs/workflows/antsibull-docs%20tests/badge.svg?event=push&branch=main)](https://github.com/ansible-community/antsibull-docs/actions?query=workflow%3A%22antsibull-docs+tests%22+branch%3Amain)\n[![Build CSS testing badge](https://github.com/ansible-community/antsibull-docs/workflows/Build%20CSS/badge.svg?event=push&branch=main)](https://github.com/ansible-community/antsibull-docs/actions?query=workflow%3A%22Build+CSS%22+branch%3Amain)\n[![Codecov badge](https://img.shields.io/codecov/c/github/ansible-community/antsibull-docs)](https://codecov.io/gh/ansible-community/antsibull-docs)\n\nTooling for building Ansible documentation.\n\nScript that is here:\n\n* antsibull-docs - Extracts documentation from ansible plugins\n\nThis also includes a [Sphinx extension](https://www.sphinx-doc.org/en/master/) `sphinx_antsibull_ext` which provides a minimal CSS file to render the output of `antsibull-docs` correctly.\n\nYou can find a list of changes in [the antsibull-docs changelog](./CHANGELOG.rst).\n\nUnless otherwise noted in the code, it is licensed under the terms of the GNU\nGeneral Public License v3 or, at your option, later.\n\nantsibull-docs is covered by the [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html).\n\n## Versioning and compatibility\n\nFrom version 1.0.0 on, antsibull-docs sticks to semantic versioning and aims at providing no backwards compatibility breaking changes **to the command line API (antsibull-docs)** during a major release cycle. We might make exceptions from this in case of security fixes for vulnerabilities that are severe enough.\n\nWe explicitly exclude code compatibility. **antsibull-docs is not supposed to be used as a library.** The only exception are dependencies with other antsibull projects (currently, only [antsibull](https://github.com/ansible-community/antsibull/) itself). If you want to use a certain part of antsibull-docs as a library, please create an issue so we can discuss whether we add a stable interface for **parts** of the Python code. We do not promise that this will actually happen though.\n\n## Running from source\n\nPlease note that to run antsibull-docs from source, you need to install some related projects adjacent to the antsibull-docs checkout.  More precisely, assuming you checked out the antsibull-docs repository in a directory `./antsibull-docs/`, you need to check out the following projects in the following locations:\n\n- [antsibull-core](https://github.com/ansible-community/antsibull-core/) needs to be checked out in `./antsibull-core/`.\n\nThis can be done as follows:\n\n    git clone https://github.com/ansible-community/antsibull-core.git\n    git clone https://github.com/ansible-community/antsibull-docs.git\n    cd antsibull-docs\n\nScripts are created by poetry at build time.  So if you want to run from a checkout, you\'ll have to run them under poetry::\n\n    python3 -m pip install poetry\n    poetry install  # Installs dependencies into a virtualenv\n    poetry run antsibull-docs --help\n\nNote: When installing a package published by poetry, it is best to use pip >= 19.0.  Installing with pip-18.1 and below could create scripts which use pkg_resources which can slow down startup time (in some environments by quite a large amount).\n\n## Using the Sphinx extension\n\nInclude it in your Sphinx configuration ``conf.py``::\n\n```\n# Add it to \'extensions\':\nextensions = [\'sphinx.ext.autodoc\', \'sphinx.ext.intersphinx\', \'notfound.extension\', \'sphinx_antsibull_ext\']\n```\n\n## Updating the CSS file for the Sphinx extension\n\nThe CSS file [sphinx_antsibull_ext/antsibull-minimal.css](https://github.com/ansible-community/antsibull-docs/blob/main/sphinx_antsibull_ext/antsibull-minimal.css) is built from [sphinx_antsibull_ext/css/antsibull-minimal.scss](https://github.com/ansible-community/antsibull-docs/blob/main/sphinx_antsibull_ext/src/antsibull-minimal.scss) using [SASS](https://sass-lang.com/) and [postcss](https://postcss.org/) using [autoprefixer](https://github.com/postcss/autoprefixer) and [cssnano](https://cssnano.co/).\n\nUse the script `build.sh` in `sphinx_antsibull_ext/css/` to build the `.css` file from the `.scss` file:\n\n```\ncd sphinx_antsibull_ext/css/\n./build-css.sh\n```\n\nFor this to work, you need to make sure that `sassc` and `postcss` are on your path and that the autoprefixer and nanocss modules are installed:\n\n```\n# Debian:\napt-get install sassc\n\n# PostCSS, autoprefixer and cssnano require nodejs/npm:\nnpm install -g autoprefixer cssnano postcss postcss-cli\n```\n\n## Creating a new release:\n\nIf you want to create a new release::\n\n    vim pyproject.toml  # Make sure version number is correct\n    vim changelogs/fragment/$VERSION_NUMBER.yml  # create \'release_summary:\' fragment\n    antsibull-changelog release --version $VERSION_NUMBER\n    git add CHANGELOG.rst changelogs\n    git commit -m "Release $VERSION_NUMBER."\n    poetry build\n    poetry publish  # Uploads to pypi.  Be sure you really want to do this\n\n    git tag $VERSION_NUMBER\n    git push --tags\n    vim pyproject.toml  # Bump the version number to X.Y.Z.post0\n    git commit -m \'Update the version number for the next release\' pyproject.toml\n    git push\n',
    'author': 'Toshio Kuratomi',
    'author_email': 'a.badger@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ansible-community/antsibull-docs',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
