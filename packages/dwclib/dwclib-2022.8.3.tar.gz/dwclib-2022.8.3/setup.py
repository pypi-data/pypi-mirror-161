# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dwclib',
 'dwclib.common',
 'dwclib.dask',
 'dwclib.numerics',
 'dwclib.patients',
 'dwclib.waves']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4,<1.5',
 'dask>=2022,<2023',
 'numba>=0.55,<0.56',
 'numpy>=1.22,<1.23',
 'pandas>=1.4,<1.5']

setup_kwargs = {
    'name': 'dwclib',
    'version': '2022.8.3',
    'description': 'Python wrapper to DataWarehouse Connect',
    'long_description': '# Overview\nPython wrapper to DataWarehouse Connect.\n-   Free software: ISC license\n\n## Installation\n`conda install -c conda-forge dwclib`\n\n`pip install dwclib`\n\nInstallation through conda greatly simplifies dependency management.\nYou can also install the in-development version with:\n\n`pip install https://framagit.org/jaj/dwclib/-/archive/master/dwclib-master.zip`\n\n## Changelog\n- 2022.6.23\n    - Convert packaging from flit to poetry\n    - Add linting and testing with nox, flake8 and safety\n    - Create scaffolding for future Sphinx documentation\n    - Fix a number of bugs in corner cases (division by zero, ...)\n    - Add a generic Dask wrapper to run custom DWC queries with Dask\n\n- 2022.3.22\n    - Convert packaging from old-style setup.py to flit\n    - Refactor: extract common code between dask and pandas version\n    - No longer relies on user defined function in the database\n    - Patients: add read_patient function to fetch a single patient\n    - Numerics: read_numerics patientids can be a list or a str. When it is a list, a MultiIndex is returned\n\n',
    'author': 'Jona Joachim',
    'author_email': 'jona@joachim.cc',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://framagit.org/jaj/dwclib',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
