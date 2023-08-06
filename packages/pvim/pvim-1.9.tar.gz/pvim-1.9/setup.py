#!/usr/bin/env python
import os
from setuptools import setup, find_packages
import pvim



setup(
    name='pvim',
    author='Intel',
    version=1.9,
    description='Pure Python Vim Implementation',
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
            'vim = pvim.entry_points.run_vim:run',
        ]
    },
)
