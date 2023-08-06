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


from os.path import abspath, isdir, isfile


def path(path_string):
    """!
    Check if path is a directory or file.
    Throw an error if it is not.

    @param path_string: path to a directory or file

    @returns absolute path to a directory or file
    """

    absolute_path = abspath(path_string)

    if isdir(absolute_path) or isfile(absolute_path):
        return absolute_path

    raise FileNotFoundError(absolute_path)


def dir_path(path_string):
    """!
    Check if path is a directory.
    Throw an error if it is not.

    @param path_string: path to a directory

    @returns absolute path to a directory
    """

    absolute_path = abspath(path_string)

    if isdir(absolute_path):
        return absolute_path

    raise NotADirectoryError(absolute_path)


def file_path(path_string):
    """!
    Check if path is a file.
    Throw an error if it is not.

    @param path_string: path to a file

    @returns absolute path to a file
    """

    absolute_path = abspath(path_string)

    if isfile(absolute_path):
        return absolute_path

    raise FileNotFoundError(absolute_path)
