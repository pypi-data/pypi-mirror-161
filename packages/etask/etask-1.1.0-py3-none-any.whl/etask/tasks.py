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


import glob
import os

from . import emacs
from . import pprint
from .task_generators import package_archives_generator, loader_generator


class Tasks:
    """!
    Class containing tasks to run.
    """

    def __init__(self, *args, verbose=False, **kwargs):
        self.emacs = emacs.Emacs(*args, **kwargs)
        self.verbose = verbose

    def elisp_compile(self, file_paths):
        """!
        Compile ELisp files.

        @param file_paths: ELisp files to compile
        """

        skip_names = [".dir-locals.el"]

        for file_path in file_paths:
            if os.path.basename(file_path) in skip_names:
                if self.verbose:
                    pprint.warning(f"Skipping: \"{file_path}\"...")
            else:
                if self.verbose:
                    pprint.info(f"Compiling: \"{file_path}\"...")

                self.emacs.eval_out(f"(byte-compile-file \"{file_path}\" 0)")

                elc_file = file_path + "c"

                if self.verbose and not os.path.exists(elc_file):
                    pprint.warning(f"File \"{elc_file}\" not produced.")

    def elisp_compile_dir(self, directory_paths):
        """!
        Compile files from directories.

        @param directory_paths: list of paths in which to compile files
        """

        for directory_path in directory_paths:
            self.elisp_compile(glob.glob(directory_path + "/*.el"))

    def elisp_clean(self, directory_paths):
        """!
        Remove compiled ELisp files form specified directories.

        @param directory_paths: list of paths to clean
        """

        for directory_path in directory_paths:
            if self.verbose:
                pprint.info(f"Cleaning: \"{directory_path}\"...")

            for elc_file in glob.glob(directory_path + "/*.elc"):
                if self.verbose:
                    pprint.info(f"  Removing: \"{elc_file}\".")

                os.remove(elc_file)

    def elisp_eval(self, expression_string):
        """!
        Evaluate a Emacs Lisp expression.

        @param expression_string: expression string to evaluate
        """

        self.emacs.eval_out(f"(princ {expression_string})")

    def autoloads(self, directory_paths):
        """!
        Create autolaods files for specified directories.

        @param directory_paths: list of paths to create autoloads from
        """

        for directory_path in directory_paths:
            directory_name = os.path.basename(directory_path)
            autoloads_file = os.path.join(
                directory_path, directory_name + "-autoloads.el")

            if self.verbose:
                pprint.info(f"Creating \"{autoloads_file}\"...")

            out_lines = self.emacs.execute(
                "--eval", "(setq make-backup-files nil)",
                "--eval",
                f"(setq generated-autoload-file \"{autoloads_file}\")",
                "-f", "batch-update-autoloads",
                f"{directory_path}")

            if self.verbose:
                pprint.std(out_lines)

    def package_delete(self, package_name):
        """!
        Delete (uninstall) a installed package.

        @param package_name: name of package to delete
        """

        if self.emacs.package_installed_p(package_name):
            if self.verbose:
                pprint.info(f"Deleting {package_name}...")

            self.emacs.eval_out(
                "(progn (require 'package) " +
                "(package-initialize) " +
                "(package-delete " +
                f"(car (alist-get '{package_name} package-alist)) t))")

            if self.verbose:
                pprint.info(f"...done deleting {package_name}.")

        elif self.verbose:
            pprint.info(f"Package {package_name} is already not installed.")

    def package_install_local(self, package_paths):
        """!
        Install specified package directories/files.

        Each one path is it's own package.

        @param package_paths: paths to packages to install
        """

        for package_path in package_paths:
            if self.verbose:
                pprint.info(f"Installing {package_path}...")

            self.emacs.eval_out(
                f"(package-install-file \"{package_path}\")",
                "-l", "package"
            )

            if self.verbose:
                pprint.info(f"...done installing {package_path}.")

    def package_install_remote(self, package_name, add_archive=False,
                               use_archive=False, refresh=True):
        """!
        Install a remote package.

        @param package_name: name of package to install
        @param add_archive: tuple containing an archive
               to consider when installing specified package
        @param use_archive: only install from the archive with specified name
        @param refresh: whether to refresh package archives
        """

        archive_dict = {
            "elpa": "https://tromey.com/elpa/",
            "gnu": "https://elpa.gnu.org/packages/",
            "melpa": "https://melpa.org/packages/",
            "org": "https://orgmode.org/elpa/"
        }

        if add_archive and add_archive != []:
            archive_dict[add_archive[0]] = add_archive[1]

        if use_archive:
            for name, url in archive_dict.items():
                if name == use_archive:
                    archive_dict = {name: url}

        if self.verbose:
            pprint.info(f"Installing {package_name}...")

        self.emacs.eval_out(
            f"(package-install '{package_name})",

            "-l", "package",

            # Unpack a generator call that produces a list of lists.
            * [item for sublist in package_archives_generator(archive_dict)
               for item in sublist],

            # Unpack maybe_print_archives.
            * (["--eval",
                "(mapcar " +
                "(lambda (l) (message \"Package archive: %s\" l)) " +
                "package-archives))"]
               if self.verbose else []),

            "--eval", "(package-initialize)",
            * (["--eval", "(package-refresh-contents)"]
               if refresh else [])
        )

        if self.verbose:
            pprint.info(f"...done installing {package_name}.")

    def load_path(self):
        """!
        Print the load path.

        The printed load path may be altered by setting
        the load_paths attribute of the Emacs object
        used by an instance of this method's class.
        """

        stdout_lines = self.emacs.eval(
            "(princ (mapconcat 'identity load-path \"\\n\"))")

        print("\n".join(sorted(stdout_lines)))

    def test(self, file_paths):
        """!
        Run ERT test on specified files.

        @param file_paths: list of files to load into tests
        """

        if self.verbose:
            pprint.info(f"Running test for: {', '.join(file_paths)}")

        self.emacs.eval_out(
            "(ert-run-tests-batch-and-exit)",

            "-l", "ert",

            # Unpack a generator call that produces a list of lists.
            * [item for sublist in loader_generator(file_paths)
               for item in sublist]
        )

    def test_dir(self, directory_paths):
        """!
        Test ELisp files in specified directories.

        @param directory_paths: list of paths in which to test files
        """

        for directory_path in directory_paths:
            if self.verbose:
                pprint.info(f"Testing directory: {directory_path}")

            self.test(glob.glob(directory_path + "/*.el"))
