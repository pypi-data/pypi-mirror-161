# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['laptrack']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0',
 'lap>=0.4.0,<0.5.0',
 'networkx>=2.6.1,<3.0.0',
 'numpy>=1.22.0,<2.0.0',
 'pandas>=1.3.1,<2.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'scipy>=1.7.0,<2.0.0',
 'typing-extensions>=3.10.0,<4.0.0']

entry_points = \
{'console_scripts': ['laptrack = laptrack.__main__:main']}

setup_kwargs = {
    'name': 'laptrack',
    'version': '0.1.7a7',
    'description': 'LapTrack',
    'long_description': "LapTrack\n========\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black| |Zenodo|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/laptrack.svg\n   :target: https://pypi.org/project/laptrack/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/laptrack.svg\n   :target: https://pypi.org/project/laptrack/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/laptrack\n   :target: https://pypi.org/project/laptrack\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/laptrack\n   :target: https://opensource.org/licenses/BSD-3-Clause\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/laptrack/latest.svg?label=Read%20the%20Docs\n   :target: https://laptrack.readthedocs.io/\n   :alt: Read the documentation at https://laptrack.readthedocs.io/\n.. |Tests| image:: https://github.com/yfukai/laptrack/workflows/Tests/badge.svg\n   :target: https://github.com/yfukai/laptrack/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/yfukai/laptrack/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/yfukai/laptrack\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n.. |Zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.5519538.svg\n   :target: https://doi.org/10.5281/zenodo.5519538\n   :alt: Zenodo\n\nFeatures\n--------\n\nProvides a robust particle tracking algorithm using the Linear Assignment Problem, with various cost functions for linking.\n\nInstallation\n------------\n\nYou can install *LapTrack* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install laptrack\n\n\nUsage\n-----\n\nPlease see the Usage_ for details.\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `The 3-Clause BSD License`_,\n*LapTrack* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\n- This program implements a modified version of the algorithm in the `K. Jaqaman et al. (2008)`_.\n\n- Inspired by TrackMate_ a lot. See documentation_ for its detailed algorithm, the `2016 paper`_, and the `2021 paper`_.\n\n- This project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.\n\n\nCitation\n--------\n\nIf you use this program for your research, please cite it and help us build more.\n\n.. code-block:: bib\n\n   @misc{laptrack,\n      author = {Yohsuke T. Fukai},\n      title = {laptrack},\n      year  = {2021},\n      url   = {https://doi.org/10.5281/zenodo.5519537},\n   }\n\n\n.. _K. Jaqaman et al. (2008): https://www.nature.com/articles/nmeth.1237\n.. _TrackMate: https://imagej.net/plugins/trackmate/\n.. _documentation: https://imagej.net/plugins/trackmate/algorithms\n.. _2016 paper: https://doi.org/10.1016/j.ymeth.2016.09.016\n.. _2021 paper: https://doi.org/10.1101/2021.09.03.458852\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _The 3-Clause BSD License: https://opensource.org/licenses/BSD-3-Clause\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/yfukai/laptrack/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://laptrack.readthedocs.io/en/latest/usage.html\n",
    'author': 'Yohsuke Fukai',
    'author_email': 'ysk@yfukai.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yfukai/laptrack',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.1,<3.11',
}


setup(**setup_kwargs)
