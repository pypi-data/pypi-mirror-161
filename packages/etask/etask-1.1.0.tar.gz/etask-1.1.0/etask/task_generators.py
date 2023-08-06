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


def package_archives_generator(archive_dict):
    """!
    Create Emacs package-archives.
    """

    for name, remote in archive_dict.items():
        yield [
            "--eval",
            f"(add-to-list 'package-archives '(\"{name}\" . \"{remote}\"))"
        ]


def loader_generator(file_paths):
    """!
    Create a list of arguments to load specified files.
    """

    for file_path in file_paths:
        yield ["-l", file_path]
