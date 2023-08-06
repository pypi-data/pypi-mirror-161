# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['metrontagger']

package_data = \
{'': ['*']}

install_requires = \
['darkseid>=1.3.3,<2.0.0',
 'mokkari>=2.3.0,<3.0.0',
 'pyxdg>=0.28,<0.29',
 'questionary>=1.10.0,<2.0.0']

entry_points = \
{'console_scripts': ['metron-tagger = metrontagger.cli:main']}

setup_kwargs = {
    'name': 'metron-tagger',
    'version': '1.2.18',
    'description': 'A program to write metadata from metron.cloud to a comic archive',
    'long_description': '=============\nMetron-Tagger\n=============\n\n.. image:: https://img.shields.io/pypi/v/metron-tagger.svg\n    :target: https://pypi.org/project/metron-tagger/\n\n.. image:: https://img.shields.io/pypi/pyversions/metron-tagger.svg\n    :target: https://pypi.org/project/metron-tagger/\n\n.. image:: https://img.shields.io/github/license/bpepple/metron-tagger\n    :target: https://opensource.org/licenses/GPL-3.0\n\n.. image:: https://codecov.io/gh/Metron-Project/metron-tagger/branch/master/graph/badge.svg?token=d8TyzWM2Uz \n    :target: https://codecov.io/gh/Metron-Project/metron-tagger\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n\nQuick Description\n-----------------\n\nA command-line tool to tag comic archives with metadata from metron.cloud_.\n\n.. _metron.cloud: https://metron.cloud\n\nInstallation\n------------\n\nPyPi\n~~~~\n\nOr install it yourself:\n\n.. code:: bash\n\n  $ pip install --user metron-tagger\n\nFAQ\n---\n\n**How to enable RAR support?**\n\n- It depends on the unrar command-line utility, and expects it to be in your $PATH.\n\nHelp\n----\n\n::\n\n  usage: metron-tagger [-h] [-r] [-o] [--id ID] [-d] [--ignore-existing] [-i] [--missing] [-s] [-e] [-z] [--delete-original] [--version] path [path ...]\n\n  Read in a file or set of files, and return the result.\n\n  positional arguments:\n    path                 Path of a file or a folder of files.\n\n  options:\n    -h, --help           show this help message and exit\n    -r, --rename         Rename comic archive from the files metadata. (default: False)\n    -o, --online         Search online and attempt to identify comic archive. (default: False)\n    --id ID              Identify file for tagging with the Metron Issue Id. (default: None)\n    -d, --delete         Delete the metadata tags from the file. (default: False)\n    --ignore-existing    Ignore files that have existing metadata tag. (default: False)\n    -i, --interactive    Interactively query the user when there are matches for an online search. (default: False)\n    --missing            List files without metadata. (default: False)\n    -s, --sort           Sort files that contain metadata tags. (default: False)\n    -e, --export-to-cb7  Export a CBZ (zip) or CBR (rar) archive to a CB7 (7zip) archive. (default: False)\n    -z, --export-to-cbz  Export a CB7 (7zip) or CBR (rar) archive to a CBZ (zip) archive. (default: False)\n    --delete-original    Delete the original archive after successful export to another format. (default: False)\n    --version            Show the version number and exit\n\n\nBugs/Requests\n-------------\n\nPlease use the `GitHub issue tracker <https://github.com/Metron-Project/metron-tagger/issues>`_ to submit bugs or request features.\n\nLicense\n-------\n\nThis project is licensed under the `GPLv3 License <LICENSE>`_.\n\n',
    'author': 'Brian Pepple',
    'author_email': 'bdpepple@gmail.com',
    'maintainer': 'Brian Pepple',
    'maintainer_email': 'bdpepple@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
