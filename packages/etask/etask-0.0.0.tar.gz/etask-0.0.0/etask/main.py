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


def parse_args():
    """
    Gather and parse CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description=f"%(prog)s - {__description__}",
        epilog=__epilog__
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
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
    subparser = parser.add_subparsers(dest="command")

    sub_autoloads = subparser.add_parser("autoloads")
    sub_autoloads.add_argument(
        "directory",
        help="Directory to generate autolaods from",
        type=path.dir_path,
        nargs="*",
        default=[getcwd()]
    )

    sub_clean = subparser.add_parser("clean")
    sub_clean.add_argument(
        "directory",
        help="Directory to clean",
        type=path.dir_path,
        nargs="*",
        default=[getcwd()]
    )

    sub_compile = subparser.add_parser("compile")
    sub_compile.add_argument("file", type=path.file_path, nargs="+")

    sub_compile_dir = subparser.add_parser("compile-dir")
    sub_compile_dir.add_argument(
        "directory",
        help="Directory to compile",
        type=path.dir_path,
        default=[getcwd()],
        nargs="*"
    )

    sub_compile_dir = subparser.add_parser("install-local")
    sub_compile_dir.add_argument(
        "path",
        help="Path to a directory or file to install",
        type=path.path,
        default=[getcwd()],
        nargs="*"
    )

    sub_install_remote = subparser.add_parser("install-remote")
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

    subparser.add_parser("load-path")
    # ^ Takes no arguments.

    sub_test = subparser.add_parser("test")
    sub_test.add_argument(
        "file",
        help="File to load",
        type=path.file_path,
        nargs="+"
    )

    sub_test_dir = subparser.add_parser("test-dir")
    sub_test_dir.add_argument(
        "directory",
        help="Directory to test",
        type=path.dir_path,
        nargs="*",
        default=[getcwd()]
    )

    args = parser.parse_args()

    return args


def main():
    """
    Main.
    """

    args = parse_args()

    if args.debug:
        pprint.debug("Running with debugging turned on!")
        pprint.debug(f"Arguments: {args}")

    emacs_instance = emacs.Emacs(
        debug=args.debug,
        interactive=args.interactive,
        load_paths=args.load_path
    )

    if args.verbose:
        pprint.pinfo(emacs_instance)

    if not args.command and args.verbose:
        pprint.info("Nothing to do.")

    elif args.command == "autoloads":
        tasks.autoloads(emacs_instance, args.verbose, args.directory)

    elif args.command == "clean":
        tasks.elisp_clean(args.verbose, args.directory)

    elif args.command == "compile":
        tasks.elisp_compile(emacs_instance, args.verbose, args.file)

    elif args.command == "compile-dir":
        tasks.elisp_compile_dir(emacs_instance, args.verbose, args.directory)

    elif args.command == "install-local":
        tasks.install_local(emacs_instance, args.verbose, args.path)

    elif args.command == "install-remote":
        tasks.install_remote(
            emacs_instance, args.verbose,
            args.package,
            add_archive=args.add, use_archive=args.use,
            refresh=args.no_refresh
        )

    elif args.command == "load-path":
        tasks.load_path(emacs_instance)

    elif args.command == "test":
        tasks.test(emacs_instance, args.verbose, args.file)

    elif args.command == "test-dir":
        tasks.test_dir(emacs_instance, args.verbose, args.directory)


if __name__ == "__main__":
    main()
