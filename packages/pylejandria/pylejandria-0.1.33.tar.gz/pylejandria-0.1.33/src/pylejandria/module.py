"""
A simple module consisting of an init function to easily generate a new
python package. It could in the future be part of a complete tool to maintain
packages.
terminal and use:
    >>> from pylejandria.module import init
    >>> init()
It will write all the necesary files and folder for an easy pypi project. You
must check each file to fill all the info.
"""

import os
from pylejandria.constants import SETUP, PYPROJECT, LICENSE
import pylejandria


def init(name: str) -> None:
    src = pylejandria.gui.ask('directory')
    if not src:
        return
    folders = [f'{src}/src', f'{src}/src/{name}', f'{src}/tests']
    files = [
        ('setup.cfg', SETUP.replace('module_name', name)),
        ('pyproject.toml', PYPROJECT),
        ('LICENSE', LICENSE),
        ('README.md', ''),
        (f'/src/{name}/__init__.py', '')
    ]
    for folder in folders:
        os.makedirs(folder)

    for file, info in files:
        with open(f'{src}/{file}', 'w') as f:
            f.write(info)


if __name__ == '__main__':
    init('Testing')
