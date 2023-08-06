# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['graphlet', 'graphlet.etl']

package_data = \
{'': ['*']}

install_requires = \
['pydantic-spark>=0.1.1,<0.2.0',
 'pydantic>=1.9.1,<2.0.0',
 'pyspark>=3.2.1,<4.0.0',
 'typeguard>=2.13.3,<3.0.0']

setup_kwargs = {
    'name': 'graphlet',
    'version': '0.1.1',
    'description': 'Graphlet AI Knowledge Graph Factory',
    'long_description': '# Graphlet AI Knowledge Graph Factory\n\n<p align="center">\n    <img src="https://github.com/Graphlet-AI/graphlet/raw/main/images/graphlet_logo.png" alt="Our mascot Orbits the Squirrel has 5 orbits. Everyone knows this about squirrels!" width="300"/>\n</p>\n\nThis is the PyPi module for the Graphlet AI Knowledge Graph Factory. Our mission is to create a Spark-based wizard for building large knowledge graphs that makes them easier to build for fewer dolalrs and with less risk.\n\n## Core Features\n\nThis project is new, some features we are building are:\n\n1) [Create a Pydantic/PySpark base class for transforming multiple entities into a uniform ontology](https://github.com/Graphlet-AI/graphlet/issues/1)\n\n2) [Create a generic, configurable system for entity resolution of heterogeneous networks](https://github.com/Graphlet-AI/graphlet/issues/3)\n\n3) [Create an efficient pipeline for computing network motifs and aggregating higher order networks](https://github.com/Graphlet-AI/graphlet/issues/5)\n\n4) [Implement efficient motif searching via neural subgraph matching](https://github.com/Graphlet-AI/graphlet/issues/4)\n\n## System Architecture\n\n![Graphlet AI System Architecture](https://github.com/Graphlet-AI/graphlet/raw/main/images/System-Architecture---From-OmniGraffle.png)\n\n## License\n\nThis project is created and published under the [Apache License, version 2.0](https://www.apache.org/licenses/LICENSE-2.0).\n\n## Conventions\n\nThis project uses pre-commit hooks to enforce its conventions: git will reject commits that don\'t comply with our various flake8 plugins.\n\nWe use [numpy docstring format](https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard) on all Python classes and functions, which is enforced by [pydocstring](https://github.com/robodair/pydocstring) and [flake8-docstrings](https://gitlab.com/pycqa/flake8-docstrings).\n\nWe run `black`, `flake8`, `isort` and `mypy` in [.pre-commit-config.yaml](.pre-commit-config.yaml). All of these are configured in [pyproject.toml](pyproject.toml) except for flake8 which uses [`.flake8`](.flake8).\nFlake8 uses the following plugins. We will consider adding any exceptions to the flake config that are warranted, but please document them in your pull requests.\n\n```toml\nflake8-docstrings = "^1.6.0"\npydocstyle = "^6.1.1"\nflake8-simplify = "^0.19.2"\nflake8-unused-arguments = "^0.0.10"\nflake8-class-attributes-order = "^0.1.3"\nflake8-comprehensions = "^3.10.0"\nflake8-return = "^1.1.3"\nflake8-use-fstring = "^1.3"\nflake8-builtins = "^1.5.3"\nflake8-functions-names = "^0.3.0"\nflake8-comments = "^0.1.2"\n```\n\n## Developer Setup\n\nThis project is in a state of development, things are still forming and changing. If you are here, it must be to contribute :)\n### Dependencies\n\nWe manage dependencies with [poetry](https://python-poetry.org/) which are managed (along with most settings) in [pyproject.toml](pyproject.toml).\n\nTo build the project, run:\n\n```bash\npoetry install\n```\n\nTo add a PyPi package, run:\n\n```bash\npoetry add <package>\n```\n\nTo add a development package, run:\n\n```bash\npoetry add --dev <package>\n```\n\nIf you do edit [pyproject.toml](pyproject.toml) you must update to regenerate [poetry.lock](poetry.lock):\n\n```bash\npoetry update\n```\n\n### Pre-Commit Hooks\n\nWe use [pre-commit](https://pre-commit.com/) to run [black](https://github.com/psf/black), [flake8](https://flake8.pycqa.org/en/latest/), [isort](https://pycqa.github.io/isort/) and [mypy](http://mypy-lang.org/). This is configured in [.pre-commit-config.yaml](.pre-commit-config.yaml).\n\n### VSCode Settings\n\nThe following [VSCode](https://code.visualstudio.com/) settings are defined for the project in [.vscode/settings.json](.vscode/settings.json) to ensure code is formatted consistent with our pre-commit hooks:\n\n```json\n{\n    "editor.rulers": [90, 120],\n    "[python]": {\n        "editor.defaultFormatter": "ms-python.python",\n        "editor.formatOnSave": true,\n        "editor.codeActionsOnSave": {"source.organizeImports": true},\n    },\n    "python.jediEnabled": false,\n    "python.languageServer": "Pylance",\n    "python.linting.enabled": true,\n    "python.formatting.provider": "black",\n    "python.sortImports.args": ["--profile", "black"],\n    "python.linting.pylintEnabled": false,\n    "python.linting.flake8Enabled": true,\n    "autoDocstring.docstringFormat": "numpy",\n}\n```\n',
    'author': 'Russell Jurney',
    'author_email': 'rjurney@graphlet.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://graphlet.ai',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
