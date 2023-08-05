#
# The MIT License (MIT)
# Copyright (c) 2021 M.O.S.S. Computer Grafik Systeme GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT,TORT OR OTHERWISE, ARISING FROM, OUT
# OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# from logging import root
from __future__ import unicode_literals

import argparse
import json
import logging
import shutil
import sys

# import os
from os import getcwd, makedirs, path

from moss.ems.emsservice import EmsServiceException, Service
from moss.ems.scripts.ems_cli_compare import EmsCliCompare
from moss.ems.scripts.ems_cli_export import EmsCliExport
from moss.ems.scripts.ems_cli_import import EmsCliImport
from moss.ems.scripts.utilities import promptutil

logger = logging.getLogger("ems_cli")

# Support python3 environment
if sys.version_info[0] >= 3:
    unicode = str


class EmsCliException(Exception):
    """
    Handles general exceptions for the command line interface
    """


class EmsCli(
    EmsCliImport,
    EmsCliExport,
    EmsCliCompare,
):
    """
    The command line interface for exporting projects
    from and importing projects to an EMS instance.
    """

    def __init__(self, ems_url, username, password):
        # type: (str, str, str) -> None

        try:
            self.ems_service = Service(ems_url, username, password)  # type: ignore
        except EmsServiceException:
            logger.exception("Error connecting to instance")
            sys.exit(1)

        self.cli_mode = True

    @staticmethod
    def json_to_file(dictionary, outpath=getcwd(), filename="", indent=None):
        """Writes a file with the given JSON data as dict

        Args:
            dictionary: the JSON data as dict
            outpath: the directory of the file
            filename: the name of the file
            indent: indent for the JSON data for pretty printing

        Returns:

        """

        if not path.exists(outpath):
            makedirs(outpath)

        filename = "{file}.json".format(file=filename)

        filepath = path.join(outpath, filename)

        with open(filepath, "w") as out_file:
            logger.info("Writing '{}'.".format(filepath))
            out_file.write(unicode(json.dumps(dictionary, indent=indent)))

    @staticmethod
    def file2json(filename):
        # type: (str) -> dict
        """Reads a file assuming JSON data

        Args:
            filename: the name of the file

        Returns:
            the JSON data as dict
        """
        try:
            with open(filename) as json_file:
                logger.info("Reading '{}'.".format(filename))
                data = json.load(json_file)
                return data
        except FileNotFoundError:
            exception = "The file '{}' does not exist".format(filename)
            raise EmsCliException(exception)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        dest="subcommands",
        title="subcommands",
        description="valid subcommands",
        help="additional help",
    )

    # Parent Parser
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--url", type=str, help="Url of the WEGA-EMS instance.")
    parent_parser.add_argument("--username", type=str, help="Username")
    parent_parser.add_argument("--password", type=str, help="Password")
    parent_parser.add_argument(
        "--interactive", action="store_true", dest="interactive", default=False
    )
    parent_parser.add_argument(
        "--logging",
        type=str,
        help="Logging Level",
        choices=["DEBUG", "INFO"],
        default="INFO",
    )

    # Export
    parser_export = subparsers.add_parser(
        "export", help="Exports a project to a directory", parents=[parent_parser]
    )
    parser_export.add_argument(
        "--project", type=str, help="The WEGA-EMS-Project to read from."
    )
    parser_export.add_argument(
        "--outpath",
        type=str,
        default=None,
        help="The directory where the exported JSON-files will be placed to.",
    )
    parser_export.add_argument(
        "--delete_outpath",
        action="store_true",
        default=False,
        help="Flag for deleting the target directory.",
    )

    parser_export.add_argument(
        "--master_filter", type=str, default=None, help="Filter for the master object"
    )

    # Import
    parser_import = subparsers.add_parser(
        "import", help="Imports a project from a directory", parents=[parent_parser]
    )
    parser_import.add_argument(
        "--project", type=str, help="The WEGA-EMS-Project to be generated."
    )
    parser_import.add_argument(
        "--inputpath",
        type=str,
        default=None,
        help="The directory where the JSON-files will be taken from.",
    )
    parser_import.add_argument(
        "--delete_project",
        action="store_true",
        default=False,
        help="Flag for deleting the project before importing.",
    )

    # Compare
    parser_compare = subparsers.add_parser(
        "compare", help="Compares two projects", parents=[parent_parser]
    )
    parser_compare.add_argument(
        "--project1", type=str, help="The first WEGA-EMS-Project to compare."
    )
    parser_compare.add_argument(
        "--project2", type=str, help="The second WEGA-EMS-Project to compare."
    )

    # This to show help if no parameter is provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    subcommands = args.subcommands

    if hasattr(args, "logging") and args.logging == "DEBUG":
        logger.info("Set logging to DEBUG")
        logger.setLevel(logging.DEBUG)

    if not args.interactive:
        promptutil.set_prompt_defaults(interactive=False)

    if args.url is None or args.url == "":
        args.url = promptutil.prompt("URL", required=True)

    if args.username is None or args.username == "":
        args.username = promptutil.prompt("Username", required=True)

    if args.password is None or args.password == "":
        args.password = promptutil.prompt("Password", required=True, is_secure=True)

    MyEmsCli = EmsCli(args.url, args.username, args.password)

    logger.info("Starting EMS_CLI ({})".format(subcommands))
    if subcommands == "export":
        kwargs = {}
        if args.project is None or args.project == "":
            args.project = promptutil.prompt("Project", required=True)

        if args.outpath is None or args.outpath == "":
            args.outpath = promptutil.prompt("Output Path", required=True)

        if path.exists(args.outpath):
            if args.delete_outpath is None or args.interactive:
                args.delete_outpath = promptutil.prompt(
                    "Delete Outpath", required=True, default=args.delete_outpath
                )

            if args.delete_outpath:
                logger.info("Removing the target directory %s", args.outpath)
                shutil.rmtree(args.outpath, ignore_errors=True)
            else:
                logger.error(
                    "Error the directory {0} exist. Please remove it.".format(
                        args.outpath
                    )
                )
                sys.exit(1)

        if args.master_filter is not None:
            kwargs["master_filter"] = args.master_filter

        MyEmsCli.ems_export(args.project, args.outpath, True, **kwargs)
    elif subcommands == "import":
        if args.project is None or args.project == "":
            args.project = promptutil.prompt("Project", required=True)

        if args.inputpath is None or args.inputpath == "":
            args.inputpath = promptutil.prompt("Input Path", required=True)

        if not args.delete_project and args.interactive:
            args.delete_project = promptutil.prompt(
                "Delete Project (y/N)?", required=True, default=False
            )

        project = next(
            (prj for prj in MyEmsCli.ems_service.projects if prj.name == args.project),
            None,
        )
        if project is not None:
            if args.delete_project:
                logger.info(
                    "Removing the target project '%s' from %s", args.project, args.url
                )
                MyEmsCli.ems_service.delete_project(args.project)
            else:
                raise EmsCliException(
                    "The target project {} already exists".format(args.outpath)
                )
        MyEmsCli.ems_import(args.project, args.inputpath)
    elif subcommands == "compare":
        if args.project1 is None or args.project1 == "":
            args.project1 = promptutil.prompt("Project 1", required=True)

        if args.project2 is None or args.project2 == "":
            args.project2 = promptutil.prompt("Project 2", required=True)

        MyEmsCli.ems_compare(args.project1, args.project2)
    logger.info("EMS_CLI completed")


if __name__ == "__main__":
    main()
