# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['_fastoad']

package_data = \
{'': ['*']}

install_requires = \
['fast-oad-core>=v1.3.5,<2.0.0', 'fast-oad-cs25<1.0.0']

setup_kwargs = {
    'name': 'fast-oad',
    'version': '1.3.5',
    'description': 'FAST-OAD is a framework for performing rapid Overall Aircraft Design',
    'long_description': '![Tests](https://github.com/fast-aircraft-design/FAST-OAD/workflows/Tests/badge.svg)\n[![Codacy Badge](https://app.codacy.com/project/badge/Grade/9691f1d1430c45cf9c94bc342b4c6122)](https://www.codacy.com/gh/fast-aircraft-design/FAST-OAD?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=fast-aircraft-design/FAST-OAD&amp;utm_campaign=Badge_Grade)\n[![codecov](https://codecov.io/gh/fast-aircraft-design/FAST-OAD/branch/master/graph/badge.svg)](https://codecov.io/gh/fast-aircraft-design/FAST-OAD)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)\n\n[![Documentation Status](https://readthedocs.org/projects/fast-oad/badge/?version=stable)](https://fast-oad.readthedocs.io/)\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/fast-aircraft-design/FAST-OAD.git/latest-release?urlpath=lab%2Ftree%2Fsrc%2Ffastoad%2Fnotebooks)\n\n\nFAST-OAD: Future Aircraft Sizing Tool - Overall Aircraft Design\n===============================================================\n\nFAST-OAD is a framework for performing rapid Overall Aircraft Design.\n\nIt proposes multi-disciplinary analysis and optimisation by relying on\nthe [OpenMDAO framework](https://openmdao.org/).\n\nFAST-OAD allows easy switching between models for a same discipline, and\nalso adding/removing/developing models to match the need of your study.\n\nMore details can be found in the [official documentation](https://fast-oad.readthedocs.io/).\n\n> **Important notice:**\n>\n> Since version 1.3.0, FAST-OAD models for commercial transport aircraft have moved in \n> package  \n> [FAST-OAD-CS25](https://pypi.org/project/fast-oad-cs25/). This package is installed along with \n> FAST-OAD, to keep backward compatibility.\n> \n> Keep in mind that any update of these models will now come through new releases of FAST-OAD-CS25.\n> \n> To get FAST-OAD without these models, you may install\n> [FAST-OAD-core](https://pypi.org/project/fast-oad-core/).\n> \n> :warning: Upgrading from an earlier version than 1.3 may break the `fastoad` command line (no \n> impact on PythonAPI). See [this issue](https://github.com/fast-aircraft-design/FAST-OAD/issues/425)\n> for details and fix.\n\nWant to try quickly?\n--------------------\nYou can run FAST-OAD tutorials **without installation** using our\n[Binder-hosted Jupyter notebooks](https://mybinder.org/v2/gh/fast-aircraft-design/FAST-OAD.git/latest-release?filepath=src%2Ffastoad%2Fnotebooks).\n\n\nInstall\n-------\n\n**Prerequisite**:FAST-OAD needs at least **Python 3.7.0**.\n\nIt is recommended (but not required) to install FAST-OAD in a virtual\nenvironment ([conda](https://docs.conda.io/en/latest/),\n[venv](https://docs.python.org/3.7/library/venv.html), ...)\n\nOnce Python is installed, FAST-OAD can be installed using pip.\n\n> **Note**: If your network uses a proxy, you may have to do [some\n> settings](https://pip.pypa.io/en/stable/user_guide/#using-a-proxy-server)\n> for pip to work correctly\n\nYou can install the latest version with this command:\n\n``` {.bash}\n$ pip install --upgrade fast-oad\n```\n\nor, if you want the minimum installation without the CS25-related models:\n\n``` {.bash}\n$ pip install --upgrade fast-oad-core\n```\n',
    'author': 'Christophe DAVID',
    'author_email': 'christophe.david@onera.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fast-aircraft-design/FAST-OAD',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
