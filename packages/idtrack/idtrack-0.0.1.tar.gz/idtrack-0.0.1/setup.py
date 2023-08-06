# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['idtrack']

package_data = \
{'': ['*']}

install_requires = \
['PyMySQL>=1.0.2,<2.0.0',
 'PyYAML>=5.4.1',
 'click>=8.0.0',
 'h5py>=3.7.0,<4.0.0',
 'networkx>=2.8.5,<3.0.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'requests>=2.28.1,<3.0.0',
 'rich>=10.3.0',
 'tables>=3.7.0,<4.0.0']

entry_points = \
{'console_scripts': ['idtrack = idtrack.__main__:main']}

setup_kwargs = {
    'name': 'idtrack',
    'version': '0.0.1',
    'description': 'Biological ID matching between different times and/or databases.',
    'long_description': 'idtrack\n===========================\n\n|PyPI| |Python Version| |License| |Read the Docs| |Build| |Tests| |Codecov| |pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/idtrack.svg\n   :target: https://pypi.org/project/idtrack/\n   :alt: PyPI\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/idtrack\n   :target: https://pypi.org/project/idtrack\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/github/license/theislab/idtrack\n   :target: https://opensource.org/licenses/BSD\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/idtrack/latest.svg?label=Read%20the%20Docs\n   :target: https://idtrack.readthedocs.io/\n   :alt: Read the documentation at https://idtrack.readthedocs.io/\n.. |Build| image:: https://github.com/theislab/idtrack/workflows/Build%20idtrack%20Package/badge.svg\n   :target: https://github.com/theislab/idtrack/actions?workflow=Package\n   :alt: Build Package Status\n.. |Tests| image:: https://github.com/theislab/idtrack/workflows/Run%20idtrack%20Tests/badge.svg\n   :target: https://github.com/theislab/idtrack/actions?workflow=Tests\n   :alt: Run Tests Status\n.. |Codecov| image:: https://codecov.io/gh/theislab/idtrack/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/theislab/idtrack\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\nFeatures\n--------\n\n* TODO\n\n\nInstallation\n------------\n\nYou can install *idtrack* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install idtrack\n\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nCredits\n-------\n\nThis package was created with cookietemple_ using Cookiecutter_ based on Hypermodern_Python_Cookiecutter_.\n\n.. _cookietemple: https://cookietemple.com\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _PyPI: https://pypi.org/\n.. _Hypermodern_Python_Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _pip: https://pip.pypa.io/\n.. _Usage: https://idtrack.readthedocs.io/en/latest/usage.html\n',
    'author': 'Kemal Inecik',
    'author_email': 'k.inecik@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/theislab/idtrack',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
