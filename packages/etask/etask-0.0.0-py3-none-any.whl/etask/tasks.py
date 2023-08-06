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

from . import pprint


def elisp_compile(emacs_instance, verbose, file_paths):
    """
    Compile ELisp files.
    """

    skip_names = [".dir-locals.el"]

    for file_path in file_paths:
        if os.path.basename(file_path) in skip_names:
            if verbose:
                pprint.warning(f"Skipping: \"{file_path}\"...")
        else:
            if verbose:
                pprint.info(f"Compiling: \"{file_path}\"...")

            emacs_instance.eval_out(f"(byte-compile-file \"{file_path}\" 0)")


def elisp_compile_dir(emacs_instance, verbose, directory_paths):
    """
    Compile files from directories.
    """

    for directory_path in directory_paths:
        elisp_compile(
            emacs_instance, verbose, glob.glob(directory_path + "/*.el"))


def elisp_clean(verbose, directory_paths):
    """
    Remove compiled ELisp files form specified directories.
    """

    for directory_path in directory_paths:
        if verbose:
            pprint.info(f"Cleaning: \"{directory_path}\"...")

        for elc_file in glob.glob(directory_path + "/*.elc"):
            if verbose:
                pprint.info(f"  Removing: \"{elc_file}\".")

            os.remove(elc_file)


def autoloads(emacs_instance, verbose, directory_paths):
    """
    Create autolaods files for specified directories.
    """

    for directory_path in directory_paths:
        directory_name = os.path.basename(directory_path)
        autoloads_file = os.path.join(
            directory_path, directory_name + "-autoloads.el")

        if verbose:
            pprint.info(f"Creating \"{autoloads_file}\"...")

        out_lines = emacs_instance.execute(
            "--eval", "(setq make-backup-files nil)",
            "--eval", f"(setq generated-autoload-file \"{autoloads_file}\")",
            "-f", "batch-update-autoloads",
            f"{directory_path}")

        if verbose:
            pprint.std(out_lines)


def package_archives_generator(archive_dict):
    """
    Create Emacs package-archives.
    """

    for name, remote in archive_dict.items():
        yield [
            "--eval",
            f"(add-to-list 'package-archives '(\"{name}\" . \"{remote}\"))"
        ]


def install_local(emacs_instance, verbose, package_paths):
    """
    Install specified package directories/files.
    Each one path is it's own package.
    """

    for package_path in package_paths:
        if verbose:
            pprint.info(f"Installing {package_path}...")

        emacs_instance.eval_out(
            f"(package-install-file \"{package_path}\")",
            "-l", "package"
        )

        if verbose:
            pprint.info(f"...done installing {package_path}.")


def install_remote(emacs_instance, verbose,
                   package_name,
                   add_archive=False, use_archive=False,
                   refresh=True):
    """
    Install a remote package.
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

    if verbose:
        pprint.info(f"Installing {package_name}...")

    emacs_instance.eval_out(
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
           if verbose else []),

        "--eval", "(package-initialize)",
        * (["--eval", "(package-refresh-contents)"]
           if refresh else [])
    )

    if verbose:
        pprint.info(f"...done installing {package_name}.")


def load_path(emacs_instance):
    """
    Print the load path.
    """

    stdout_lines = emacs_instance.eval(
        "(princ (mapconcat 'identity load-path \"\\n\"))")

    print("\n".join(sorted(stdout_lines)))


def loader_generator(file_paths):
    """
    Create a list of arguments to load specified files.
    """

    for file_path in file_paths:
        yield ["-l", file_path]


def test(emacs_instance, verbose, file_paths):
    """
    Run ERT test on specified files.
    """

    if verbose:
        pprint.info(f"Running test for: {', '.join(file_paths)}")

    emacs_instance.eval_out(
        "(ert-run-tests-batch-and-exit)",

        "-l", "ert",

        # Unpack a generator call that produces a list of lists.
        * [item for sublist in loader_generator(file_paths)
           for item in sublist]
    )


def test_dir(emacs_instance, verbose, directory_paths):
    """
    Test ELisp files in specified directories.
    """

    for directory_path in directory_paths:
        if verbose:
            pprint.info(f"Testing directory: {directory_path}")

        test(emacs_instance, verbose, glob.glob(directory_path + "/*.el"))
