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


import subprocess

from shutil import which

from . import pprint


class Emacs:
    """!
    The Emacs class.

    Used to create disposable Emacs processes.
    """

    def __init__(self, debug=False,
                 extra=False, interactive=False, load_paths=False):
        self.debug = debug
        self.extra = extra or []
        self.interactive = interactive
        self.load_paths = load_paths or []
        self.executable_path = which("emacs")

    def execute(self, *args):
        """!
        Execute GNU Emacs with args.

        @returns Tuple with keys "stderr" and "stdout"
        """

        command = [self.executable_path]

        for load_path in self.load_paths:
            command.extend(["-L", load_path])

        command.extend(self.extra)
        command.extend([*args])

        if self.interactive:
            command.extend([
                "--eval", "(sleep-for 2)",  # It's interactive mode anyway.
                "--eval", "(kill-emacs)"
            ])
        else:
            command.append("--batch")

        if self.debug:
            pprint.debug(f"{pprint.YELLOW}$_{pprint.RESET} {repr(command[0])}")

            for arg in command[1:]:
                pprint.debug(f"   {repr(arg)}")

        captured_output = subprocess.run(
            command, capture_output=True, check=False)

        stdout_lines = captured_output.stdout.decode("UTF-8").split("\n")
        stderr_lines = captured_output.stderr.decode("UTF-8").split("\n")

        if captured_output.returncode != 0:
            for stderr_line in stderr_lines:
                pprint.warning(stderr_line)

            raise RuntimeError(f"Command exited with error, was: {command}")

        return {"stderr": stderr_lines, "stdout": stdout_lines}

    def eval(self, expression_string, *args):
        """!
        Evaluate an expression, return output as lines.

        @param expression_string: expression string to evaluate

        @return Lines that are the standard output of calling GNU Emacs
        """

        std_lines = self.execute("-q", *args, "--eval", expression_string)
        stdout_lines = std_lines["stdout"]

        return stdout_lines

    def eval_princ(self, expression_string, *args):
        """!
        Eval surrounded with "princ" function.

        To ease calling for value.

        @param expression_string: expression string to evaluate

        @returns Lines that are the standard output of calling GNU Emacs
        """

        return self.eval(f"(princ {expression_string})", *args)

    def eval_out(self, expression_string, *args):
        """!
        Evaluate an expression, print any output.

        To ease calling for efect.

        @param expression_string: expression string to evaluate
        """

        std_lines = self.execute("-q", *args, "--eval", expression_string)

        pprint.std(std_lines)

    def get_version(self):
        """!
        Get the version of GNU Emacs.

        @returns String containing GNU Emacs version
        """

        stdout_lines = self.eval_princ(
            "emacs-version",
            # Always in this "bare" mode, because we want just the version :)
            "-Q", "--batch"
        )
        emacs_version = stdout_lines[0]

        return emacs_version

    def package_installed_p(self, package_name):
        """!
        Check if a package is installed.

        @param package_name: package name

        @returns Boolean - True is installed, False if not
        """

        stdout_lines = self.eval_princ(
            "(progn (require 'package) " +
            "(package-initialize) " +
            f"(package-installed-p '{package_name}))")

        return "t" in stdout_lines
