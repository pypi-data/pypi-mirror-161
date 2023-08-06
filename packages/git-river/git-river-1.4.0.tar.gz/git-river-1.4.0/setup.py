# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['git_river', 'git_river.commands', 'git_river.ext', 'git_river.tests']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.27,<4.0.0',
 'PyGithub>=1.55,<2.0',
 'appdirs>=1.4.4,<2.0.0',
 'click>=8.0.4,<9.0.0',
 'colorama>=0.4.4,<0.5.0',
 'giturlparse>=0.10.0,<0.11.0',
 'inflect>=5.4.0,<6.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-gitlab>=3.2.0,<4.0.0',
 'structlog>=21.5.0,<22.0.0']

entry_points = \
{'console_scripts': ['git-river = git_river.cli:main']}

setup_kwargs = {
    'name': 'git-river',
    'version': '1.4.0',
    'description': 'Tools for working with upstream repositories',
    'long_description': 'git river\n=========\n\n`git-river` is a tool designed to make it easier to work with large\nnumbers of GitHub and GitLab projects and "forking" workflow that involve\npulling changes from "upstream" repositories and pushing to "downstream"\nrepositories. \n\n`git-river` will manage a "workspace" path you configure, cloning repositories\ninto that directory with a tree-style structure organised by domain, project\nnamespace, and project name.\n\n```\n$ tree ~/workspace\n~/workspace\n├── github.com\n│   └── datto\n│       └── git-river\n└── gitlab.com\n    └── datto\n        └── git-river\n```\n\nLinks\n-----\n\n* [Source code](https://github.com/datto/git-river/)\n* [Packages](https://pypi.org/project/git-river/)\n\nInstallation\n------------\n\n`git-river` requires Python 3.9 or above.\n\n```\npip3 install git-river\n```\n\nUsage\n-----\n\nRun `git-river <subcommand>`. Git\'s builtin aliasing also allows you to\nrun `git river` instead.\n\nBefore you can use `git-river` you must configure a workspace path by running\n`git-river init PATH` or setting the `GIT_RIVER_WORKSPACE` environment variable.\nThis should point to a directory `git-river` can use to clone git repositories\ninto.\n\nSeveral commands will attempt to discover various names, and usually have an\noption flag to override discovery.\n\n- The "upstream" remote is the first of `upstream` or `origin` that exists. Override with `--upstream`.\n- The "downstream" remote is the first of `downstream` that exists. Override with `--downstream`.\n- The "mainline" branch is the first of `main` or `master` that exists. Override with `--mainline`.\n\n### Subcommands\n\n- `git river clone URL...` clones a repository into the workspace path.\n\n- `git river config` manages the configuration file.\n\n  - `git river config display` prints the loaded configuration as JSON. Credentials are redacted.\n  - `git river config init` creates an initial config file.\n  - `git river config workspace` prints the workspace path.\n\n- `git river forge` manages repositories listed by GitHub and GitLab.\n\n  - `git river forge` runs the `clone` + `archived` + `configure` + `remotes` subcommands.\n  - `git river forge clone` clones repositories.\n  - `git river forge configure` sets git config options.\n  - `git river forge fetch` fetches each git remote.\n  - `git river forge list` displays remote repositories that will be cloned.\n  - `git river forge remotes` sets `upstream`+`downstream` or `origin` remotes.\n  - `git river forge tidy` deletes branches merged into the mainline branch.\n  - `git river forge archived` lists archived repositories that exist locally.\n\n- `git river` also provides some "loose" subcommands that work on the repository\n  in the current directory, mostly matching the features from the `forge`\n  subcommand.\n\n  - `git river fetch` fetches all git remotes.\n  - `git river merge` creates the merge result of all `feature/*` branches.\n  - `git river tidy` deletes branches merged into the mainline branch.\n  - `git river restart` rebases the current branch from the upstream remotes mainline branch.\n\nConfiguration\n-------------\n\nConfiguration is a JSON object read from `~/.config/git-river/config.json`. Run\n`git-river config init` to create an example configuration file.\n\n- `path` - path to a directory to use as the "workspace".\n- `forges` - a map of forges.\n\nForges have the following options. Only `type` is required - the default\nconfiguration is to use the main public GitHub or GitLab domain without\nauthentication.\n\n- `type` (required) - The type of the instance, either `github` or `gitlab`.\n- `base_url` (optional) - Base url of the instance. Should not include a trailing slash.\n  - Default for GitHub instances is `https://api.github.com`.\n  - Default for GitLab instances is `https://gitlab.com`.\n- `login_or_token` (optional, GitHub only) - Authentication token.\n- `private_token` (optional, GitLab only) - Authentication token.\n- `gitconfig` (default: `{}`) - A key-value map of git config options to set on repositories.\n- `groups` (default: `[]`) - Include repositories from specific groups.\n- `users` (default: `[]`) - Include repositories from specific users.\n- `self` (default: `true`) - Automatically include the authenticated user\'s repositories.\n\n\n### Example\n\n```json\n{\n  "workspace": "~/Development",\n  "forges": {\n    "gitlab": {\n      "type": "gitlab",\n      "base_url": "https://gitlab.com",\n      "private_token": "...",\n      "groups": [],\n      "users": [],\n      "self": true,\n      "gitconfig": {\n        "user.email": "user+gitlab@example.invalid"\n      }\n    },\n    "github": {\n      "type": "github",\n      "login_or_token": "...",\n      "groups": [],\n      "users": [],\n      "gitconfig": {\n        "user.email": "user+github@example.invalid"\n      }\n    }\n  }\n}\n```\n\nDevelopment\n-----------\n\n[Poetry][poetry] is used to develop, build, and package git-river. Poetry\'s\n[documentation][poetry/docs] describes how to install it on your OS. Once you\'ve\ninstalled it, create a virtual environment containing git-river and it\'s\ndependencies with `poetry install`.\n\nYou can then run the local version of the CLI with `poetry run git-river`.\n\nCode is formatted using [black], run with `poetry run black git_river`.\n\nTypes are checked using [mypy], run with `poetry run mypy git_river`.\n\nTests are written using [pytest], run with `poetry run pytest`.\n\n```bash\n# Download the project and install dependencies\ngit clone https://github.com/datto/git-river.git\ncd git-river\npoetry install\n\n# Use the local version of the CLI\npoetry run git-river ...\n\n# Test, lint and format code\npoetry run black git_river\npoetry run mypy git_river\npoetry run pytest\n```\n\nLicense\n-------\n\nLicensed under the Mozilla Public License Version 2.0.\n\nCopyright Datto, Inc.\n\nAuthored by [Sam Clements](https://github.com/borntyping).\n\n[black]: https://github.com/psf/black\n[mypy]: https://mypy.readthedocs.io/en/stable/\n[poetry/docs]: https://python-poetry.org/docs/\n[poetry]: https://python-poetry.org/\n[pytest]: https://docs.pytest.org/\n',
    'author': 'Sam Clements',
    'author_email': 'sclements@datto.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/git-river/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
