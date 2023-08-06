# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pandas_or', 'pandas_or.binning', 'pandas_or.data', 'pandas_or.routing']

package_data = \
{'': ['*'], 'pandas_or.data': ['binning/*', 'routing/*']}

install_requires = \
['ortools>=9.3.10497,<10.0.0', 'pandas>=1.2.0,<2.0.0']

setup_kwargs = {
    'name': 'pandas-or',
    'version': '0.1.0',
    'description': 'Operations research with Ortools and Pandas.',
    'long_description': '# Pandas OR\n\n![Python version](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue.svg)\n[![PyPI version](https://badge.fury.io/py/pandas-or.svg)](https://pypi.org/project/pandas-or/)\n[![PyPI download](https://img.shields.io/pypi/dm/pandas-or.svg)](https://pypi.org/project/pandas-or/#files)\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/lucasjamar/pandas-or/HEAD?labpath=examples)\n[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/lucasjamar/pandas-or/blob/main/LICENSE.md)\n\nOperations research made easy using [Pandas](https://pandas.pydata.org/) and [Ortools](https://developers.google.com/optimization).\n\nThe purpose of working with Pandas in combination with Ortools is to bridge the gap between\noperations research and data analytics, data science, and data visualization.\nWith pandas-or, you can solve complex knapsack or vehicle routing type problems and then create\nstatistics, plots, and dashboards from your results!\n\n## &#x1F4BB; Installation\n\n### Pip\n\n```\npip install pandas-or\n```\n\n## &#x25B6; Demo\n\nTry out the examples in Binder!\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/lucasjamar/pandas-or/HEAD?labpath=examples)\n\n\n## &#x1F6B6; Upcoming features\n\n- Code tests.\n- Basic shift scheduling solvers.\n- More complex routing problem solvers (pickups & deliveries, constraints).\n- Read The Docs documentation.\n- Gitlab CI builds.\n\n## &#x1F4DA; Read The Docs\n\nComing soon!',
    'author': 'lucas.jamar',
    'author_email': 'lucasjamar@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lucasjamar/pandas-or',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
