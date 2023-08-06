# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['integrity']

package_data = \
{'': ['*']}

install_requires = \
['beet>=0.63.1', 'bolt>=0.16', 'mecha>=0.48.1']

setup_kwargs = {
    'name': 'integrity',
    'version': '0.9.0',
    'description': 'Development facilities for the bolt environment',
    'long_description': '# Integrity\n\n[![GitHub Actions](https://github.com/thewii/integrity/workflows/CI/badge.svg)](https://github.com/thewii/integrity/actions)\n[![PyPI](https://img.shields.io/pypi/v/integrity.svg)](https://pypi.org/project/integrity/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/integrity.svg)](https://pypi.org/project/integrity/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![Discord](https://img.shields.io/discord/900530660677156924?color=7289DA&label=discord&logo=discord&logoColor=fff)](https://discord.gg/98MdSGMm8j)\n\n> Development facilities for the bolt environment\n\n```python\nfrom integrity import Component\n\nfrom ./settings import settings\nfrom ./blocks import blocks\nfrom ./player import player\n\nmain = Component()\n\nfunction main.on("main"):\n    if score settings.data.activated obj matches 1:\n        main.run("active")\n\nfunction main.on("active"):\n    as @a at @s:\n        player.run("main")\n\nfunction blocks.on("placed_by_player"):\n    if block ~ ~ ~ stone expand:\n        say Placed stone!\n        player.run("placed_stone")\n```\n\n## Installation\n\nThe package can be installed with `pip`. Note, you must have\nboth `beet` and `mecha` installed to use this package.\n\n```bash\n$ pip install integrity\n```\n\n## Getting Started\n\nTo use this package, we must add the plugin to the `require`\nsection in the `beet` project file alongside with `mecha` and\n`bolt`.\n\n```yaml\nrequire:\n    - bolt\n    - integrity\npipeline:\n    - mecha\n```\n\nNow that we\'ve enabled `integrity`, we can import the module\ndirectly inside a bolt script\n\n```python\nfrom integrity import Component\n\nfoo = Component("foo")\n```\n\n## Features\n\n- Components\n\n## Contributing\n\nContributions are welcome. Make sure to first open an issue\ndiscussing the problem or the new feature before creating a\npull request. The project uses [`poetry`](https://python-poetry.org).\n\n```bash\n$ poetry install\n```\n\nYou can run the tests with `poetry run pytest`.\n\n```bash\n$ poetry run pytest\n```\n\nThe project must type-check with [`pyright`](https://github.com/microsoft/pyright).\nIf you\'re using VSCode the [`pylance`](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)\nextension should report diagnostics automatically. You can also install\nthe type-checker locally with `npm install` and run it from the command-line.\n\n```bash\n$ npm run watch\n$ npm run check\n```\n\nThe code follows the [`black`](https://github.com/psf/black) code style.\nImport statements are sorted with [`isort`](https://pycqa.github.io/isort/).\n\n```bash\n$ poetry run isort bolt_expressions examples tests\n$ poetry run black bolt_expressions examples tests\n$ poetry run black --check bolt_expressions examples tests\n```\n\n---\n\nLicense - [MIT](https://github.com/rx-modules/bolt-expressions/blob/main/LICENSE)\n',
    'author': 'TheWii',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thewii/integrity',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
