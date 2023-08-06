#!/usr/bin/env python3


"""
Main entry-point to ETask.
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


import argparse

from os import getcwd

from . import (
    __description__,
    __epilog__,
    __version__,
    emacs,
    path,
    pprint,
    tasks
)
from .pinfo import pinfo


def extract_summary(function):
    """!
    Extract function summary from doxygen form.

    @param function: function object to be called

    @returns summary string
    """

    return function.__doc__.splitlines()[1]


def make_parser():
    """!
    Return argument parser for CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description=f"etask - {__description__}",
        epilog=__epilog__
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"etask {__version__}"
    )
    parser.add_argument(
        "-D", "--debug",
        help="Turn on debugging options",
        action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Increase verbosity",
        action="store_true"
    )
    parser.add_argument(
        "-L", "--load-path",
        help="Add a directory to load-path",
        type=path.dir_path,
        action="append"
    )
    parser.add_argument(
        "-i", "--interactive",
        help="Run in interactive mode (non-batch)",
        action="store_true"
    )
    parser.add_argument(
        "-e", "--extra",
        help="Additional arguments to Emacs (eg. --extra=\"-nw\")",
        action="append"
    )
    subparser = parser.add_subparsers(dest="command")

    sub_autoloads = subparser.add_parser(
        "autoloads",
        help=extract_summary(tasks.Tasks.autoloads)
    )
    sub_autoloads.add_argument(
        "directory",
        help="Directory to generate autolaods from",
        type=path.dir_path,
        nargs="*",
        default=[getcwd()]
    )

    sub_clean = subparser.add_parser(
        "clean",
        help=extract_summary(tasks.Tasks.elisp_clean)
    )
    sub_clean.add_argument(
        "directory",
        help="Directory to clean",
        type=path.dir_path,
        nargs="*",
        default=[getcwd()]
    )

    sub_compile = subparser.add_parser(
        "compile",
        help=extract_summary(tasks.Tasks.elisp_compile)
    )
    sub_compile.add_argument(
        "file",
        help="Emacs Lisp source file to compile",
        type=path.file_path,
        nargs="+"
    )

    sub_compile_dir = subparser.add_parser(
        "compile-dir",
        help=extract_summary(tasks.Tasks.elisp_compile_dir)
    )
    sub_compile_dir.add_argument(
        "directory",
        help="Directory with Emacs Lisp source files to compile",
        type=path.dir_path,
        default=[getcwd()],
        nargs="*"
    )

    sub_delete = subparser.add_parser(
        "delete",
        help=extract_summary(tasks.Tasks.package_delete)
    )
    sub_delete.add_argument(
        "package",
        help="Package to delete",
        type=str,
    )

    sub_eval = subparser.add_parser(
        "eval",
        help=extract_summary(tasks.Tasks.elisp_eval)
    )
    sub_eval.add_argument(
        "expression",
        help="Emacs Lisp expression to evaluate",
        type=str
    )

    sub_install_local = subparser.add_parser(
        "install-local",
        help=extract_summary(tasks.Tasks.package_install_local)
    )
    sub_install_local.add_argument(
        "path",
        help="Path to a directory or file to install",
        type=path.path,
        default=[getcwd()],
        nargs="*"
    )

    sub_install_remote = subparser.add_parser(
        "install-remote",
        help=extract_summary(tasks.Tasks.package_install_remote)
    )
    sub_install_remote.add_argument(
        "-a", "--add",
        help="Add a package archive (requires: name and URL)",
        type=str,
        nargs=2,
        default=False
    )
    sub_install_remote.add_argument(
        "-u", "--use",
        help="Use only the selected package archive",
        type=str,
        default=False
    )
    sub_install_remote.add_argument(
        "-n", "--no-refresh",
        help="Do not download descriptions of configured package archives",
        action="store_false"
    )
    sub_install_remote.add_argument("package", type=str)

    subparser.add_parser(
        "load-path",
        help=extract_summary(tasks.Tasks.load_path)
    )
    # ^ Takes no arguments.

    sub_test = subparser.add_parser(
        "test",
        help=extract_summary(tasks.Tasks.test)
    )
    sub_test.add_argument(
        "file",
        help="File to load",
        type=path.file_path,
        nargs="+"
    )

    sub_test_dir = subparser.add_parser(
        "test-dir",
        help=extract_summary(tasks.Tasks.test_dir)
    )
    sub_test_dir.add_argument(
        "directory",
        help="Directory to test",
        type=path.dir_path,
        nargs="*",
        default=[getcwd()]
    )

    return parser


def main():
    """!
    Main.
    """

    parser = make_parser()
    args = parser.parse_args()

    if args.debug:
        pprint.debug("Running with debugging turned on!")
        pprint.args(args)

    emacs_tasks = tasks.Tasks(
        debug=args.debug,
        extra=args.extra,
        interactive=args.interactive,
        load_paths=args.load_path,
        verbose=args.verbose
    )

    if args.verbose:
        pinfo(emacs.Emacs(debug=args.debug))

    if not args.command and args.verbose:
        pprint.info("Nothing to do.")

    elif args.command == "autoloads":
        emacs_tasks.autoloads(args.directory)

    elif args.command == "clean":
        emacs_tasks.elisp_clean(args.directory)

    elif args.command == "compile":
        emacs_tasks.elisp_compile(args.file)

    elif args.command == "compile-dir":
        emacs_tasks.elisp_compile_dir(args.directory)

    elif args.command == "delete":
        emacs_tasks.package_delete(args.package)

    elif args.command == "eval":
        emacs_tasks.elisp_eval(args.expression)

    elif args.command == "install-local":
        emacs_tasks.package_install_local(args.path)

    elif args.command == "install-remote":
        emacs_tasks.package_install_remote(
            args.package,
            add_archive=args.add,
            use_archive=args.use,
            refresh=args.no_refresh
        )

    elif args.command == "load-path":
        emacs_tasks.load_path()

    elif args.command == "test":
        emacs_tasks.test(args.file)

    elif args.command == "test-dir":
        emacs_tasks.test_dir(args.directory)


if __name__ == "__main__":
    main()
