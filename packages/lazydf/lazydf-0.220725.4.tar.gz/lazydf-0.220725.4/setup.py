# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['lazydf']

package_data = \
{'': ['*']}

install_requires = \
['orjson>=3.7.8,<4.0.0', 'pymongo>=4.2.0,<5.0.0']

setup_kwargs = {
    'name': 'lazydf',
    'version': '0.220725.4',
    'description': 'Hopefully safe and deterministic serializer to binary format, including Pandas data',
    'long_description': '![test](https://github.com/lazydf/lazydf/workflows/test/badge.svg)\n[![codecov](https://codecov.io/gh/lazydf/lazydf/branch/main/graph/badge.svg)](https://codecov.io/gh/lazydf/lazydf)\n<a href="https://pypi.org/project/lazydf">\n<img src="https://img.shields.io/github/v/release/lazydf/lazydf?display_name=tag&sort=semver&color=blue" alt="github">\n</a>\n![Python version](https://img.shields.io/badge/python-3.10-blue.svg)\n[![license: GPL v3](https://img.shields.io/badge/License-GPLv3_%28ask_for_options%29-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)\n[![API documentation](https://img.shields.io/badge/doc-API%20%28auto%29-a0a0a0.svg)](https://lazydf.github.io/lazydf)\n\n\n# lazydf - Serialization of nested objects to binary format \nAn alternative to pickle, but may use pickle if safety is not needed.\n\nPrinciple: Start from the simplest and safest possible and try to be fast.\n* try orjson\n  * `dict`, `str`, `int`, etc\n* try bson\n  * standard types accepted by mongodb\n* serialize as numpy\n  * ndarray, pandas dataframe/series\n\nNon-deterministic and unsafe modes (pickle) are planned for the near future. \n \n\n\n## Python installation\n### from package\n```bash\n# Set up a virtualenv. \npython3 -m venv venv\nsource venv/bin/activate\n\n# Install from PyPI\npip install lazydf\n```\n\n### from source\n```bash\ngit clone https://github.com/lazydf/lazydf\ncd lazydf\npoetry install\n```\n\n### Examples\nSome usage examples.\n\n\n\n\n## Grants\nThis work was partially supported by Fapesp under supervision of\nProf. André C. P. L. F. de Carvalho at CEPID-CeMEAI (Grants 2013/07375-0 – 2019/01735-0).\n',
    'author': 'davips',
    'author_email': 'dpsabc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
