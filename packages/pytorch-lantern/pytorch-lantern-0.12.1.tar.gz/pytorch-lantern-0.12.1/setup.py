# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lantern']

package_data = \
{'': ['*']}

install_requires = \
['imgaug>=0.4.0,<0.5.0',
 'numpy>=1.19.4,<2.0.0',
 'opencv-python>=4.4.0,<5.0.0',
 'pytorch-datastream>=0.4.0,<0.5.0',
 'tensorboard>=2.2.0,<3.0.0',
 'torch>=1.6.0,<2.0.0',
 'tqdm>=4.51.0,<5.0.0']

setup_kwargs = {
    'name': 'pytorch-lantern',
    'version': '0.12.1',
    'description': 'Pytorch project template and related tools',
    'long_description': '================\nPytorch Lantern\n================\n\n.. image:: https://badge.fury.io/py/pytorch-lantern.svg\n       :target: https://badge.fury.io/py/pytorch-lantern\n\n.. image:: https://img.shields.io/pypi/pyversions/pytorch-lantern.svg\n       :target: https://pypi.python.org/pypi/pytorch-lantern\n\n.. image:: https://readthedocs.org/projects/pytorch-lantern/badge/?version=latest\n       :target: https://pytorch-lantern.readthedocs.io/en/latest/?badge=latest\n\n.. image:: https://img.shields.io/pypi/l/pytorch-lantern.svg\n       :target: https://pypi.python.org/pypi/pytorch-lantern\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n\nLantern contains our process of bringing a project to fruition as\nefficiently as possible. This is subject to change as we iterate and improve.\nThis package implements tools and missing features to help bridge the gap\nbetween frameworks and libraries that we utilize.\n\nThe main packages and tools that we build around are:\n\n- `pytorch <https://pytorch.org>`_\n- `pytorch-datastream <https://github.com/Aiwizo/pytorch-datastream>`_\n- `guild <https://guild.ai>`_\n\n\nSee the `documentation <https://pytorch-lantern.readthedocs.io/en/latest/>`_\nfor more information.\n\nCreate new project with template\n================================\n\nInstall `cookiecutter <https://github.com/cookiecutter/cookiecutter>`_\nand `poetry <https://github.com/python-poetry/poetry>`_:\n\n.. code-block::\n\n    pip install cookiecutter\n    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python\n\nSetup project:\n\n.. code-block::\n\n    cookiecutter https://github.com/aiwizo/pytorch-lantern-template.git\n    cd <new-project>\n    poetry install\n\nYou can now train the placeholder model and inspect the results:\n\n.. code-block::\n\n    guild run prepare\n    guild run train\n    guild tensorboard\n\nUse lantern without templates\n==============================\n\nInstall lantern from pypi using pip or poetry:\n\n.. code-block::\n\n    poetry add pytorch-lantern\n    # pip install pytorch-lantern\n',
    'author': 'Aiwizo',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Aiwizo/pytorch-lantern',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
