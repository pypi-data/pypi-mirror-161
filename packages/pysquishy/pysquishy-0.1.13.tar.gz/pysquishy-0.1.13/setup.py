# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysquishy', 'pysquishy.libwrap']

package_data = \
{'': ['*']}

install_requires = \
['coloredlogs>=15.0.1,<16.0.0', 'lief>=0.12.1,<0.13.0']

setup_kwargs = {
    'name': 'pysquishy',
    'version': '0.1.13',
    'description': 'LLVM pass wrapper library for creating robust shellcode',
    'long_description': '# squishy 🐻\u200d❄️\n\nA collection of new (LLVM 15) passes to compile normal-looking code to a callable, jump-to-able blob. Also includes a python library that provides\na python interface to produce a blob for any architecture triple.\n\nInspired by SheLLVM, but should address some of the outdated issues with\nthat project. Thanks to SheLLVM for the inspiration :)\n\n## Installing\n\nThe easiest way to install `squishy 🐻\u200d❄️` is from PyPi (sorry about the name, PyPi has weird rules). If an sdist is installed, `meson` must be installed and\n`llvm-15` must be available.\n\n```\npython3 -m pip install pysquishy\n```\n\n## Building\n\n`squishy 🐻\u200d❄️` uses the [meson](https://mesonbuild.com) modern build system. To\nbuild, first ensure that `meson` and `ninja` are installed, and that you have\nan installation of `llvm-15` which you can get [here](https://apt.llvm.com).\n\nThen, invoke:\n\n```\nmeson build\ncd build\nmeson compile\n```\n\nto produce the [library](build/src/libsquishy.so).\n\n\n## Passes\n\n1. Aggressive Inliner: Recursively applies alwaysinline and inlines function\n  calls and global variables into the main function.',
    'author': 'novafacing',
    'author_email': 'rowanbhart@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
