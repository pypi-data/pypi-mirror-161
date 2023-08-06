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


import colorama


colorama.init(autoreset=True)


BLUE = colorama.Fore.BLUE
GREEN = colorama.Fore.GREEN
MAGENTA = colorama.Fore.MAGENTA
RED = colorama.Fore.RED
WHITE = colorama.Fore.WHITE
YELLOW = colorama.Fore.YELLOW

BRIGHT = colorama.Style.BRIGHT
RESET = colorama.Fore.RESET + colorama.Style.RESET_ALL


def debug(string):
    """!
    Debug print.

    @param: string to print
    """

    print(f"  {BRIGHT}{WHITE}[{YELLOW}***{WHITE}]{RESET}: {string}")


def info(string):
    """!
    Debug print.

    @param: string to print
    """

    print(f"  {BRIGHT}{WHITE}[{GREEN}...{WHITE}]{RESET}: {string}")


def warning(string):
    """!
    Debug print.

    @param: string to print
    """

    print(f"  {BRIGHT}{WHITE}[{RED}!!!{WHITE}]{RESET}: {string}")


def std(std_lines):
    """!
    Helper to print "stdout" and "stderr" from std_lines.

    @param: dict of lines to print
    """

    for stdout_line in std_lines["stdout"]:
        if stdout_line != "":
            info(stdout_line)

    for stdout_line in std_lines["stderr"]:
        if stdout_line != "":
            warning(stdout_line)


def args(namespace):
    """!
    Pretty-print args from a given namespace.

    @param: args namespace to print
    """

    for option, value in vars(namespace).items():

        if value is True:
            color = GREEN
        elif value is False:
            color = RED
        elif value is None:
            color = BLUE
        else:
            color = WHITE

        debug(f"{BRIGHT}{WHITE}{option}{RESET}: {color}{value}{RESET}")
