#!/usr/bin/env python
import os
from setuptools import setup, find_packages
import vim



setup(
    name='pvim',
    author='Intel',
    version=vim.__version__,
    description='Pure Python Vi Implementation',
    packages=find_packages('.'),
    install_requires = [
        'prompt_toolkit>=2.0.0,<3.1.0',
        'six',
        'pyflakes',        # For Python error reporting.
        'pygments',        # For the syntax highlighting.
        'docopt',          # For command line arguments.
    ],
    entry_points={
        'console_scripts': [
            'vim = vi.entry_points.run_vim:run',
        ]
    },
)
