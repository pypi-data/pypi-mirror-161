# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['shelchemy']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.39,<2.0.0', 'lz4>=4.0.2,<5.0.0', 'temporenc>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'shelchemy',
    'version': '0.220726.7',
    'description': 'Shelve-like dict using sqlachemy as backend, and lazy scheduler for resuming tasks',
    'long_description': '![test](https://github.com/shelchemy/shelchemy/workflows/test/badge.svg)\n[![codecov](https://codecov.io/gh/shelchemy/shelchemy/branch/main/graph/badge.svg)](https://codecov.io/gh/shelchemy/shelchemy)\n<a href="https://pypi.org/project/shelchemy">\n<img src="https://img.shields.io/github/v/release/shelchemy/shelchemy?display_name=tag&sort=semver&color=blue" alt="github">\n</a>\n![Python version](https://img.shields.io/badge/python-3.8%20%7C%203.9-blue.svg)\n[![license: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)\n\n[![API documentation](https://img.shields.io/badge/doc-API%20%28auto%29-a0a0a0.svg)](https://shelchemy.github.io/shelchemy)\n\n\n# shelchemy - Dict-like (shelve-like) storage wrapper for any DBMS (SQLAlchemy)\n \n\n\n## Python installation\n### from package\n```bash\n# Set up a virtualenv. \npython3 -m venv venv\nsource venv/bin/activate\n\n# Install from PyPI\npip install shelchemy\n```\n\n### from source\n```bash\ngit clone https://github.com/shelchemy/shelchemy\ncd shelchemy\npoetry install\n```\n\n### Examples\nSome usage examples.\n\n\n## Grants\nThis work was partially supported by Fapesp under supervision of\nProf. André C. P. L. F. de Carvalho at CEPID-CeMEAI (Grants 2013/07375-0 – 2019/01735-0).\n',
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
