# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clin', 'clin.clients', 'clin.models']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0',
 'colorama>=0.4,<0.5',
 'deepdiff>=5.7,<6.0',
 'pygments>=2.11,<3.0',
 'pyyaml>=6.0,<7.0',
 'requests>=2.27,<3.0']

entry_points = \
{'console_scripts': ['clin = clin.run:cli']}

setup_kwargs = {
    'name': 'clin',
    'version': '1.6.0',
    'description': 'Cli for Nakadi resources management in Infrastructure as Code style',
    'long_description': '# Clin\n\n**Clin** is a command-line utility to manage [Nakadi](https://nakadi.io/)\nresources from schema files in "Infrastructure as Code" style.\n![](https://github.com/zalando-incubator/clin/raw/master/docs/gifs/demo.gif)\n\n## User Guide\n\n### Prerequisites\n\n* [Python](https://www.python.org/) >= 3.7\n\n### Installing\nYou can install **clin** directly from [PyPI](https://pypi.org/project/clin/)\nusing pip:\n\n```bash\npip install clin\n```\n\n### Getting started\n\nAfter this you should be able to run the `clin` tool:\n```bash\n~ clin --help\nUsage: clin [OPTIONS] COMMAND [ARGS]...\n...\n```\n\nPlease refer to the [documentation](https://github.com/zalando-incubator/clin/tree/master/docs)\nand [examples](https://github.com/zalando-incubator/clin/tree/master/docs/examples).\n\n## Contributing\n\nPlease read [CONTRIBUTING](https://github.com/zalando-incubator/clin/blob/master/CONTRIBUTING.md)\nfor details on our process for submitting pull requests to us, and please ensure\nyou follow the [CODE_OF_CONDUCT](https://github.com/zalando-incubator/clin/blob/master/CODE_OF_CONDUCT.md).\n\n### Prerequisites\n\n* [Python](https://www.python.org/) >= 3.7\n* [Poetry](https://python-poetry.org/) for packaging and dependency\n  management. See the [official docs](https://python-poetry.org/docs/) for\n  instructions on installation and basic usage.\n\n### Installing\nAfter cloning the repository, use `poetry` to create a new virtual environment\nand restore all dependencies.\n\n```bash\npoetry install\n```\n\nIf you\'re using an IDE (eg. PyCharm), make sure that it\'s configured to use the\nvirtual environment created by poetry as the project\'s interpreter. You can find\nthe path to the used environment with `poetry env info`.\n\n### Running the tests\n\n```bash\npoetry run pytest\n```\n\n## Versioning\n\nWe use [SemVer](http://semver.org) for versioning. For the versions available,\nsee the [tags on this repository](https://github.com/zalando-incubator/clin/tags).\n\n## Authors\n\n* **Dmitry Erokhin** [@Dmitry-Erokhin](https://github.com/Dmitry-Erokhin)\n* **Daniel Stockhammer** [@dstockhammer](https://github.com/dstockhammer)\n\nSee also the list of [contributors](Chttps://github.com/zalando-incubator/clin/blob/master/ONTRIBUTORS.md)\nwho participated in this project.\n\n## License\n\nThis project is licensed under the MIT License. See the\n[LICENSE](https://github.com/zalando-incubator/clin/blob/master/LICENSE) file\nfor details.\n',
    'author': 'Dmitry Erokhin',
    'author_email': 'dmitry.erokhin@zalando.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zalando-incubator/clin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
