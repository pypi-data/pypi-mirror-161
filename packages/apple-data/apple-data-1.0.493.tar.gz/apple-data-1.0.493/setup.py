# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['apple_data']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'apple-data',
    'version': '1.0.493',
    'description': 'Static data from https://docs.hackdiffe.rent',
    'long_description': "# Apple Hardware Data\n\nBrought to you by the [Hack Different](https://hackdifferent.com) team.\n\n## Introduction\n\nThis is a package with data files sourced from\nthe [Hack Different - Apple Knowledge](https://github.com/hack-different/apple-knowledge/tree/main/_data)\nrepository.  Updates to that repository will automatically update this package, therefore no attempt should\nbe made to update the data files by any other method.\n\n## Accessing the Data\n\nFor the time being, there is only one simple API:\n\n```python\nfrom apple_data import get_data\n\nREGISERS = get_data('registers')\n```\n\n## Credits\n\n* [Hack Different](https://hackdifferent.com)\n\nCreated and maintained as a labor of love by [`rickmark`](https://github.com/rickmark)",
    'author': 'Rick Mark',
    'author_email': 'rickmark@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
