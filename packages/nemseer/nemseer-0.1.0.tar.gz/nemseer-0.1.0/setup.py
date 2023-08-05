# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nemseer', 'nemseer.dl_helpers']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21,<22',
 'beautifulsoup4>=4,<5',
 'dask>=2022.7.1,<2023.0.0',
 'netCDF4>=1.6.0,<2.0.0',
 'numpy>=1.23.0,<2.0.0',
 'packaging>=21.3,<22.0',
 'pandas>=1.2,<2.0',
 'pyarrow>=8.0.0,<9.0.0',
 'requests>=2,<3',
 'tqdm>=4.64.0,<5.0.0',
 'xarray>=2022,<2023']

setup_kwargs = {
    'name': 'nemseer',
    'version': '0.1.0',
    'description': 'A package for downloading and handling forecasts for the National Electricity Market (NEM) from the Australian Energy Market Operator (AEMO).',
    'long_description': "# nemseer\n\n[![Documentation Status](https://readthedocs.org/projects/nemseer/badge/?version=latest)](https://nemseer.readthedocs.io/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/UNSW-CEEM/NEMSEER/branch/master/graph/badge.svg?token=BO69YSQIGI)](https://codecov.io/gh/UNSW-CEEM/NEMSEER)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nA package for downloading and handling forecasts for the National Electricity Market (NEM) from the Australian Energy Market Operator (AEMO).\n\n## Work in Progress\n\nThis package is a work in progress. For a high-level overview of development, check out the [roadmap](ROADMAP.md).\n\n## Installation\n\n- TODO\n\n## Usage\n\n- TODO\n\n## Contributing\n\nInterested in contributing? Check out the [contributing guidelines](CONTRIBUTING.md), which also includes steps to install `nemseer` for development.\n\nPlease note that this project is released with a [Code of Conduct](CONDUCT.md). By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`nemseer` was created by Abhijith Prakash. It is licensed under the terms of the [BSD 3-Clause license](LICENSE).\n\n## Credits\n\n`nemseer` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n\n`nemseer` borrows functionality from [`NEMOSIS`](https://github.com/UNSW-CEEM/NEMOSIS), a package for extracting historical *actual* market data from AEMO's NemWeb.\n",
    'author': 'Abhijith Prakash',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
