#!/usr/bin/env python3


"""
"""  """

This file is part of python-etask.

python-etask is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3.

python-etask is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with python-etask.  If not, see <https://www.gnu.org/licenses/>.

Copyright (c) 2022, Maciej Barć <xgqt@riseup.net>
Licensed under the GNU GPL v3 License
SPDX-License-Identifier: GPL-3.0-only
"""


from setuptools import setup

from etask import __description__
from etask import __version__


setup(
    name="etask",
    version=__version__,
    description=__description__,
    author="Maciej Barć",
    author_email="xgqt@riseup.net",
    url="https://gitlab.com/xgqt/python-etask",
    license="GPL-3",
    keywords="emacs",
    python_requires=">=3.6.*",
    install_requires=["colorama"],
    packages=["etask"],
    include_package_data=True,
    zip_safe=False,
    entry_points={"console_scripts": ["etask = etask.main:main"]},
)
