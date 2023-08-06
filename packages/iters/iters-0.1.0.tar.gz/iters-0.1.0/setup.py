# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iters']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=4.3.0']

extras_require = \
{'concurrent': ['anyio>=3.6.1']}

setup_kwargs = {
    'name': 'iters',
    'version': '0.1.0',
    'description': 'Composable external iteration.',
    'long_description': '# `iters`\n\n[![License][License Badge]][License]\n[![Version][Version Badge]][Package]\n[![Downloads][Downloads Badge]][Package]\n[![Discord][Discord Badge]][Discord]\n\n[![Documentation][Documentation Badge]][Documentation]\n[![Check][Check Badge]][Actions]\n[![Test][Test Badge]][Actions]\n[![Coverage][Coverage Badge]][Coverage]\n\n> *Composable external iteration.*\n\nIf you have found yourself with a *collection* of some kind, and needed to perform\nan operation on the elements of said collection, you will quickly run into *iterators*.\nIterators are heavily used in idiomatic Python code, so becoming familiar with them is essential.\n\n## Installing\n\n**Python 3.7 or above is required.**\n\n### pip\n\nInstalling the library with `pip` is quite simple:\n\n```console\n$ pip install iters\n```\n\nAlternatively, the library can be installed from source:\n\n```console\n$ git clone https://github.com/nekitdev/iters.git\n$ cd iters\n$ python -m pip install .\n```\n\n### poetry\n\nYou can add `iters` as a dependency with the following command:\n\n```console\n$ poetry add iters\n```\n\nOr by directly specifying it in the configuration like so:\n\n```toml\n[tool.poetry.dependencies]\niters = "^0.1.0"\n```\n\nAlternatively, you can add it directly from the source:\n\n```toml\n[tool.poetry.dependencies.iters]\ngit = "https://github.com/nekitdev/iters.git"\n```\n\n## Examples\n\n### Simple\n\nSquaring only even numbers in some sequence:\n\n```python\nfrom iters import iter\n\n\ndef is_even(value: int) -> bool:\n    return not value % 2\n\n\ndef square(value: int) -> int:\n    return value * value\n\n\nnumbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]\n\nresult = iter(numbers).filter(is_even).map(square).list()\n\nprint(result)  # [0, 4, 16, 36, 64]\n```\n\n### Asynchronous\n\nAsynchronous iteration is fully supported by `iters`, and its API is similar to its\nsynchronous counterpart.\n\n## Documentation\n\nYou can find the documentation [here][Documentation].\n\n## Support\n\nIf you need support with the library, you can send an [email][Email]\nor refer to the official [Discord server][Discord].\n\n## Changelog\n\nYou can find the changelog [here][Changelog].\n\n## Security Policy\n\nYou can find the Security Policy of `iters` [here][Security].\n\n## Contributing\n\nIf you are interested in contributing to `iters`, make sure to take a look at the\n[Contributing Guide][Contributing Guide], as well as the [Code of Conduct][Code of Conduct].\n\n## License\n\n`iters` is licensed under the MIT License terms. See [License][License] for details.\n\n[Email]: mailto:support@nekit.dev\n\n[Discord]: https://nekit.dev/discord\n\n[Actions]: https://github.com/nekitdev/iters/actions\n\n[Changelog]: https://github.com/nekitdev/iters/blob/main/CHANGELOG.md\n[Code of Conduct]: https://github.com/nekitdev/iters/blob/main/CODE_OF_CONDUCT.md\n[Contributing Guide]: https://github.com/nekitdev/iters/blob/main/CONTRIBUTING.md\n[Security]: https://github.com/nekitdev/iters/blob/main/SECURITY.md\n\n[License]: https://github.com/nekitdev/iters/blob/main/LICENSE\n\n[Package]: https://pypi.org/project/iters\n[Coverage]: https://codecov.io/gh/nekitdev/iters\n[Documentation]: https://nekitdev.github.io/iters\n\n[Discord Badge]: https://img.shields.io/badge/chat-discord-5865f2\n[License Badge]: https://img.shields.io/pypi/l/iters\n[Version Badge]: https://img.shields.io/pypi/v/iters\n[Downloads Badge]: https://img.shields.io/pypi/dm/iters\n\n[Documentation Badge]: https://github.com/nekitdev/iters/workflows/docs/badge.svg\n[Check Badge]: https://github.com/nekitdev/iters/workflows/check/badge.svg\n[Test Badge]: https://github.com/nekitdev/iters/workflows/test/badge.svg\n[Coverage Badge]: https://codecov.io/gh/nekitdev/iters/branch/main/graph/badge.svg\n',
    'author': 'nekitdev',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/nekitdev/iters',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
