# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyaud_plugins', 'pyaud_plugins._plugins']

package_data = \
{'': ['*']}

install_requires = \
['Sphinx>=4.3.2,<5.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'black>=21.12,<23.0',
 'codecov>=2.1.12,<3.0.0',
 'constcheck>=0,<1',
 'coverage>=6.2,<7.0',
 'docformatter>=1.4,<2.0',
 'docsig>=0,<1',
 'environs>=9.4.0,<10.0.0',
 'flynt>=0.75,<0.77',
 'isort>=5.10.1,<6.0.0',
 'm2r>=0.2.1,<0.3.0',
 'mistune<=0.8.4',
 'mypy>=0.930,<0.972',
 'object-colors>=2.0.1,<3.0.0',
 'pipfile-requirements>=0.3.0,<0.4.0',
 'pylint>=2.12.2,<3.0.0',
 'pytest-cov>=3.0.0,<4.0.0',
 'pytest>=6.2.5,<8.0.0',
 'python-dotenv>=0.19.2,<0.21.0',
 'readmetester>=1.0.1,<3.0.0',
 'sphinxcontrib-fulltoc>=1.2.0,<2.0.0',
 'sphinxcontrib-programoutput>=0.17,<0.18',
 'toml-sort>=0.20.0,<0.21.0',
 'toml>=0.10.2,<0.11.0',
 'vulture>=2.3,<3.0']

setup_kwargs = {
    'name': 'pyaud-plugins',
    'version': '0.8.0',
    'description': 'Plugin package for Pyaud',
    'long_description': 'pyaud-plugins\n=============\n.. image:: https://img.shields.io/badge/License-MIT-yellow.svg\n    :target: https://opensource.org/licenses/MIT\n    :alt: License\n.. image:: https://img.shields.io/pypi/v/pyaud-plugins\n    :target: https://img.shields.io/pypi/v/pyaud-plugins\n    :alt: pypi\n.. image:: https://github.com/jshwi/pyaud-plugins/actions/workflows/ci.yml/badge.svg\n    :target: https://github.com/jshwi/pyaud-plugins/actions/workflows/ci.yml\n    :alt: CI\n.. image:: https://github.com/jshwi/pyaud-plugins/actions/workflows/codeql-analysis.yml/badge.svg\n    :target: https://github.com/jshwi/pyaud-plugins/actions/workflows/codeql-analysis.yml\n    :alt: CodeQL\n.. image:: https://codecov.io/gh/jshwi/pyaud-plugins/branch/master/graph/badge.svg\n    :target: https://codecov.io/gh/jshwi/pyaud-plugins\n    :alt: codecov.io\n.. image:: https://readthedocs.org/projects/pyaud-plugins/badge/?version=latest\n    :target: https://pyaud-plugins.readthedocs.io/en/latest/?badge=latest\n    :alt: readthedocs.org\n.. image:: https://img.shields.io/badge/python-3.8-blue.svg\n    :target: https://www.python.org/downloads/release/python-380\n    :alt: python3.8\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n    :alt: black\n\nPlugin package for Pyaud\n------------------------\n\nDependencies\n------------\n\n``pip install pyaud``\n\nInstall\n-------\n\n``pip install pyaud-plugins``\n\nDevelopment\n-----------\n\n``poetry install``\n\nUsage\n-----\n\nSee `pyaud <https://github.com/jshwi/pyaud#pyaud>`_\n\nPlugins\n-------\n\n``pyaud`` will automatically load this package on search for all packages prefixed with `"pyaud_"`\n\nFor writing plugins see `docs <https://jshwi.github.io/pyaud/pyaud.html#pyaud-plugins>`_\n\nThis package contains the following plugins on running `pyaud modules`\n\n.. code-block:: console\n\n    const           -- Check code for repeat use of strings\n    coverage        -- Run package unit-tests with `pytest` and `coverage`\n    deploy          -- Deploy package documentation and test coverage\n    deploy-cov      -- Upload coverage data to `Codecov`\n    deploy-docs     -- Deploy package documentation to `gh-pages`\n    docs            -- Compile package documentation with `Sphinx`\n    doctest         -- Run `doctest` on all code examples\n    doctest-package -- Run `doctest` on package\n    doctest-readme  -- Run `doctest` on Python code-blocks in README\n    files           -- Audit project data files\n    format          -- Audit code with `Black`\n    format-docs     -- Format docstrings with `docformatter`\n    format-str      -- Format f-strings with `flynt`\n    imports         -- Audit imports with `isort`\n    lint            -- Lint code with `pylint`\n    readme          -- Parse, test, and assert RST code-blocks\n    requirements    -- Audit requirements.txt with Pipfile.lock\n    sort-pyproject  -- Sort pyproject.toml file with `toml-sort`\n    test            -- Run all tests\n    tests           -- Run the package unit-tests with `pytest`\n    toc             -- Audit docs/<NAME>.rst toc-file\n    typecheck       -- Typecheck code with `mypy`\n    unused          -- Audit unused code with `vulture`\n    whitelist       -- Check whitelist.py file with `vulture`\n',
    'author': 'jshwi',
    'author_email': 'stephen@jshwisolutions.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
