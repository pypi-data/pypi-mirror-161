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


from sys import version_info

import colorama

from . import __description__, __epilog__, __version__


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
    """
    Debug print.
    """

    print(f"  {BRIGHT}{WHITE}[{YELLOW}***{WHITE}]{RESET}: {string}")


def info(string):
    """
    Debug print.
    """

    print(f"  {BRIGHT}{WHITE}[{GREEN}...{WHITE}]{RESET}: {string}")


def warning(string):
    """
    Debug print.
    """

    print(f"  {BRIGHT}{WHITE}[{RED}!!!{WHITE}]{RESET}: {string}")


def std(std_lines):
    """
    Helper to print "stdout" and "stderr" from std_lines.
    """

    for stdout_line in std_lines["stdout"]:
        if stdout_line != "":
            info(stdout_line)

    for stdout_line in std_lines["stderr"]:
        if stdout_line != "":
            warning(stdout_line)


def pinfo(emacs_instance):
    """
    Print short info about the program.
    """

    python_version = f"{version_info.major}.{version_info.minor}"

    try:
        emacs_version = emacs_instance.get_version()
    except RuntimeError:
        emacs_version = "unknown"

    print(
        f"{BRIGHT}{GREEN}ETask{RESET}, " +
        f"{__description__}, version {GREEN}{__version__}{RESET}, " +
        f"running on {BRIGHT}{BLUE}Python {python_version}{RESET} " +
        f"and {BRIGHT}{MAGENTA}GNU Emacs {emacs_version}{RESET}"
    )
    print(__epilog__)
