# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tidy', 'tidy.tests']

package_data = \
{'': ['*']}

install_requires = \
['click>7.0',
 'formaldict>0.2.0',
 'jinja2>2.10.3',
 'packaging>20.0',
 'python-dateutil>2.8.1',
 'pyyaml>5.1.2',
 'requests>2.22.0']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['importlib_metadata>=4']}

entry_points = \
{'console_scripts': ['git-tidy = tidy.cli:tidy',
                     'git-tidy-commit = tidy.cli:commit',
                     'git-tidy-lint = tidy.cli:lint',
                     'git-tidy-log = tidy.cli:log',
                     'git-tidy-squash = tidy.cli:squash']}

setup_kwargs = {
    'name': 'git-tidy',
    'version': '1.1.4',
    'description': 'Tidy git commit messages, linting, and logging',
    'long_description': "git-tidy\n########\n\n``git-tidy`` is a set of git extensions for:\n\n1. Keeping your git logs tidy with ease. ``git tidy-commit`` guides\n   users through a structured commit with a configurable schema.\n   ``git tidy-squash`` squashes messy commits into one tidy commit.\n2. Linting a commit log. ``git tidy-lint`` verifies that commits\n   match the schema. If a user uses ``git tidy-commit``, commits\n   will *always* validate.\n3. Rendering a commit log. ``git tidy-log`` can render commits from\n   any range and can render structured commits from a configurable\n   `Jinja <https://jinja.palletsprojects.com/en/2.11.x/>`__ template.\n   Want to automatically generate release notes? ``git tidy-log`` can\n   be configured to group and render commits based on the schema.\n\n.. image:: https://raw.githubusercontent.com/jyveapp/git-tidy/master/docs/_static/tidy-commit.gif\n    :width: 600\n\nDocumentation\n=============\n\n`View the git-tidy docs here\n<https://git-tidy.readthedocs.io/>`_ for a complete tutorial on using\n``git-tidy``.\n\nInstallation\n============\n\n``git-tidy`` can be installed a number of ways. The preferred way\non OSX is with `homebrew <brew.sh>`__ ::\n\n    brew tap jyveapp/homebrew-tap\n    brew install git-tidy\n\nIf not on OSX, one can install ``git-tidy`` system-wide with\n`pipx <https://github.com/pipxproject/pipx>`__::\n\n    pipx install git-tidy\n\n``git-tidy`` can also be installed with pip. Be sure to install it system-wide\nso that ``git-tidy``'s execution is not tied to a virtual environment::\n\n    pip3 install git-tidy\n\n\n.. note::\n\n  ``git-tidy`` depends on git at a version of 2.22 or higher. OSX\n  users can upgrade to the latest ``git`` version with\n  `homebrew <brew.sh>`__ using ``brew install git``.\n\n\nContributing Guide\n==================\n\nFor information on setting up git-tidy for development and\ncontributing changes, view `CONTRIBUTING.rst <CONTRIBUTING.rst>`_.\n\nPrimary Authors\n===============\n\n- @wesleykendall (Wes Kendall)\n- @tomage (Tómas Árni Jónasson)\n",
    'author': 'Wes Kendall',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Opus10/git-tidy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4',
}


setup(**setup_kwargs)
