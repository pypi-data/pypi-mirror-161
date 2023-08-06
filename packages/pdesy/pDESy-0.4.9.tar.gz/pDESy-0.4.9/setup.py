# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pDESy', 'pDESy.model']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.0,<10.0.0',
 'codecov>=2.1.12,<3.0.0',
 'coverage>=6.3.2,<7.0.0',
 'decorator>=5.1.1,<6.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'networkx>=2.8,<3.0',
 'numpy>=1.22.4,<2.0.0',
 'plotly>=5.8.2,<6.0.0',
 'poetry>=1.1.13,<2.0.0',
 'pytest-cov>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'pdesy',
    'version': '0.4.9',
    'description': 'pDESy: Discrete Event Simulation of Python',
    'long_description': "# pDESy: Discrete-Event Simulator in Python\n\n[![PyPi version](https://pypip.in/v/pDESy/badge.png)](https://pypi.org/project/pDESy/)\n[![Anaconda-Server Badge](https://anaconda.org/taiga4112/pdesy/badges/version.svg)](https://anaconda.org/taiga4112/pdesy)\n![test](https://github.com/pDESy/pDESy/workflows/test/badge.svg)\n[![codecov](https://codecov.io/gh/pDESy/pDESy/branch/master/graph/badge.svg)](https://codecov.io/gh/pDESy/pDESy)\n\n## What is it?\n\n**pDESy** is a Python package of Discrete-Event Simulator (DES). It aims to be the fundamental high-level building block for doing practical, real world engineering project management by using DES and other DES modeling tools. **pDESy** has only the function of discrete-event simulation, does not include the function of visual modeling.\n\n\n## Where to get it\nThe source code is currently hosted on GitHub at: [https://github.com/pDESy/pDESy](https://github.com/pDESy/pDESy)\n\nBinary installers for the latest released version will be available at the Python package index. Now, please install pDESy as following.\n\n```sh\npip install pDESy\n# pip install git+ssh://git@github.com/pDESy/pDESy.git # INSTALL FROM GITHUB\n# conda install -c conda-forge -c taiga4112 pDESy # INSTALL FROM ANACONDA\n```\n\n## License\n[MIT](https://github.com/pDESy/pDESy/blob/master/LICENSE)\n\n## Documentation\nAPI Documentation is [https://pDESy.github.io/pDESy/index.html](https://pDESy.github.io/pDESy/index.html).\n\n## Background\n**pDESy** is developed by a part of next generation DES tool of **[pDES](https://github.com/pDESy/pDES)**.\n\n## Contribution\n1. Fork it ( http://github.com/pDESy/pDESy/fork )\n2. Create your feature branch (git checkout -b my-new-feature)\n3. Commit your changes (git commit -am 'Add some feature')\n4. Push to the branch (git push origin my-new-feature)\n5. Create new Pull Request\n\nIf you want to join this project as a researcher, please contact [me](https://github.com/taiga4112).",
    'author': 'Taiga MITSUYUKI',
    'author_email': 'mitsuyuki-taiga-my@ynu.ac.jp',
    'maintainer': 'Taiga MITSUYUKI',
    'maintainer_email': 'mitsuyuki-taiga-my@ynu.ac.jp',
    'url': 'https://github.com/pDESy/pDESy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
