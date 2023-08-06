# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['idasen']

package_data = \
{'': ['*']}

install_requires = \
['bleak>=0.15,<0.16', 'pyyaml>=5.3.1,<7', 'voluptuous>=0.12,<0.14']

entry_points = \
{'console_scripts': ['idasen = idasen.cli:main']}

setup_kwargs = {
    'name': 'idasen',
    'version': '0.9.0',
    'description': 'ikea IDÅSEN desk API and CLI.',
    'long_description': 'idasen\n######\n\n|PyPi Version| |Build Status| |Documentation Status| |Black|\n\nThis is a heavily modified fork of `rhyst/idasen-controller`_.\n\nThe IDÅSEN is an electric sitting standing desk with a Linak controller sold by\nikea.\n\nThe position of the desk can controlled by a physical switch on the desk or\nvia bluetooth using an phone app.\n\nThis is a command line interface written in python to control the Idasen via\nbluetooth from a desktop computer.\n\nSet Up\n******\n\nPrerequisites\n=============\n\nThe desk should be connected and paired to the computer.\n\nInstall\n=======\n\n.. code-block:: bash\n\n    python3.8 -m pip install --upgrade idasen\n\nConfiguration\n*************\nConfiguration that is not expected to change frequently can be provided via a\nYAML configuration file located at ``~/.config/idasen/idasen.yaml``.\n\nYou can use this command to initialize a new configuartion file:\n\n.. code-block:: bash\n\n    idasen init\n\n.. code-block:: yaml\n\n    mac_address: AA:AA:AA:AA:AA:AA\n    positions:\n        sit: 0.75\n        stand: 1.1\n\nConfiguartion options:\n\n* ``mac_address`` - The MAC address of the desk. This is required.\n* ``positions`` - A dictionary of positions with values of desk height from the\n  floor in meters, ``sit`` and ``stand`` are provided as examples.\n\nThe program will try to find the device address,\nbut if it fails, it has to be done manually.\n\nThe device MAC addresses can be found using ``blueoothctl`` and bluetooth\nadapter names can be found with ``hcitool dev`` on linux.\n\nUsage\n*****\n\nCommand Line\n============\n\nTo print the current desk height:\n\n.. code-block:: bash\n\n    idasen height\n\nTo monitor for changes to height:\n\n.. code-block:: bash\n\n    idasen monitor\n\nTo save the current height as the sitting position:\n\n.. code-block:: bash\n\n    idasen save sit\n\nTo delete the saved sitting position:\n\n.. code-block:: bash\n\n    idasen delete sit\n\nAssuming the config file is populated to move the desk to sitting position:\n\n.. code-block:: bash\n\n    idasen sit\n\nCommunity\n*********\n\nRelated projects and packaging:\n\n* Arch Linux package: https://aur.archlinux.org/packages/idasen/\n* NixOS package: https://search.nixos.org/packages?channel=unstable&show=idasen&query=idasen\n* idasen-rest-bridge: https://github.com/huserben/idasen-rest-bridge\n\n.. _poetry: https://python-poetry.org/\n.. _install poetry: https://python-poetry.org/docs/#installation\n.. _rhyst/idasen-controller: https://github.com/rhyst/idasen-controller\n\n.. |PyPi Version| image:: https://badge.fury.io/py/idasen.svg\n   :target: https://badge.fury.io/py/idasen\n.. |Build Status| image:: https://github.com/newAM/idasen/workflows/Tests/badge.svg\n   :target: https://github.com/newAM/idasen/actions\n.. |Documentation Status| image:: https://readthedocs.org/projects/idasen/badge/?version=latest\n   :target: https://idasen.readthedocs.io/en/latest/?badge=latest\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n',
    'author': 'Alex Martens',
    'author_email': 'alex@thinglab.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/newAM/idasen',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
