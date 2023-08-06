# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_workspace',
 'poetry_workspace.commands',
 'poetry_workspace.commands.workspace',
 'poetry_workspace.schemas',
 'poetry_workspace.vcs']

package_data = \
{'': ['*']}

install_requires = \
['poetry>=1.2.0b3,<2.0.0']

entry_points = \
{'poetry.application.plugin': ['poetry-workspace-plugin = '
                               'poetry_workspace.plugin:WorkspacePlugin']}

setup_kwargs = {
    'name': 'poetry-workspace-plugin2',
    'version': '0.5.6',
    'description': 'Multi project workspace plugin for Poetry',
    'long_description': '# Poetry Workspace Plugin\n\nThis experimental tool is a [Poetry Plugin](https://python-poetry.org/docs/master/plugins) to support workflows in a multi-project repository.\n\n## Installation\n\nMake sure you are using at least Poetry 1.2.0b3. To install this preview release, run:\n\n```shell\ncurl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python - --preview\n```\n\nInstall this plugin:\n\n```shell\npoetry plugin add poetry-workspace-plugin2\n```\n\n### Why plugin2?\n\nThe [original package](https://pypi.org/project/poetry-workspace-plugin/) was released by [Martin Liu](https://pypi.org/user/martinxsliu/), a former OpenDoor employee. Before he left, he [re-released the project](https://pypi.org/project/poetry-workspace-plugin2/) under the [OpenDoor PyPI account](https://pypi.org/user/opendoor/).\n\n## Workspace\n\nA workspace is a collection of Poetry projects that share a single environment.\n\n## Example config to place at the root\n\n```\n[tool.poetry]\nname = "code"\nversion = "0.1.0"\ndescription = "Opendoor Python workspace"\nauthors = ["Developers <developers@opendoor.com>"]\n\n[[tool.poetry.source]]\nname = "pypi-local"\nurl = "https://opendoor.jfrog.io/opendoor/api/pypi/pip/simple"\nsecondary = true\n\n[tool.poetry.workspace]\ninclude = [\n  "lib/**",\n  "workspace/**",\n]\nexclude = [\n  "lib/dev-tools",\n  "lib/legacy",\n  "lib/template/**",\n]\n\n# IMPORTANT: This pyproject.toml file declares dependencies for the shared Python\n# workspace. If your app does not belong to the\n# workspace (i.e. not included in the `include` section above) then do not add your\n# app dependencies here, it will have no effect. Even if your app does belong to\n# the workspace, prefer adding app specific dependencies in your app\'s project. This\n# section is reserved for workspace level constraints.\n[tool.poetry.dependencies]\npython = "~3.9"\nvirtualenv = "^20.10.0"\n\n[tool.poetry.dev-dependencies]\n"opendoor.dev-tools" = {path = "lib/dev-tools", develop = true}\n"opendoor.tools" = {path = "tools", develop = true}\n```\n',
    'author': 'Martin Liu',
    'author_email': 'martin.xs.liu@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
