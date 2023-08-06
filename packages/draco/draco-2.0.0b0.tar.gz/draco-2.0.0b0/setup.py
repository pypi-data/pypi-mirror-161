# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['draco']

package_data = \
{'': ['*'], 'draco': ['asp/*', 'asp/examples/*']}

install_requires = \
['clingo>=5.5.2,<6.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'pandas>=1.4.2,<2.0.0',
 'scikit-learn>=1.1.1,<2.0.0']

setup_kwargs = {
    'name': 'draco',
    'version': '2.0.0b0',
    'description': 'Visualization recommendation using constraints',
    'long_description': '<p align="center">\n   <a href="https://github.com/cmudig/draco2">\n      <picture>\n         <source media="(prefers-color-scheme: dark)" srcset="https://github.com/cmudig/draco2/raw/main/docs/logo-light.png">\n         <source media="(prefers-color-scheme: light)" srcset="https://github.com/cmudig/draco2/raw/main/docs/logo-dark.png">\n         <img alt="The Draco logo. A set of circles connected by lines depicting the draco star constellation." src="https://github.com/cmudig/draco2/raw/main/docs/logo-light.png" width=260>\n      </picture>\n   </a>\n</p>\n\n# Draco v2\n\n[![Test](https://github.com/cmudig/draco2/actions/workflows/test.yml/badge.svg)](https://github.com/cmudig/draco2/actions/workflows/test.yml)\n[![code style black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![codecov](https://codecov.io/gh/cmudig/draco2/branch/main/graph/badge.svg)](https://codecov.io/gh/cmudig/draco2)\n[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/cmudig/draco2.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cmudig/draco2/context:python)\n\n**Work in Progress**\n\nDraco is a formal framework for representing design knowledge about effective visualization design as a collection of constraints. You can use Draco to find effective visualization visual designs or validate visualization designs. Draco\'s constraints are implemented in based on Answer Set Programming (ASP) and solved with the Clingo constraint solver. We also implemented a way to learn weights for the recommendation system directly from the results of graphical perception experiment. Draco v2 is a much imprived version of the first iteration of [Draco](https://github.com/uwdata/draco).\n\n## Documentation\n\nRead about Draco in the online book at https://dig.cmu.edu/draco2/. In the documentation, we just refer to _Draco_ without a version.\n\n## What\'s different from [Draco v1](https://github.com/uwdata/draco)?\n\n- Draco v2 is completely written in Python. No more need to run both Python and Node. We still use ASP for the knowledge base.\n- Generalized and extended chart specification format. The new format is more extensible with custom properties.\n- Suport for multiple views and view compostion.\n- High test-coverage, documentation, and updated development tooling.\n\n## Contributing\n\nWe welcome any input, feedback, bug reports, and contributions. You can learn about setting up your development environment in [CONTRIBUTING.md](https://github.com/cmudig/draco2/blob/main/CONTRIBUTING.md).\n',
    'author': 'Dominik Moritz',
    'author_email': 'domoritz@cmu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cmudig/draco2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<3.10',
}


setup(**setup_kwargs)
