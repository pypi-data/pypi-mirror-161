# -*- coding: utf-8 -*-

"""

dryjq.cli

Command line interface

Copyright (C) 2022 Rainer Schwarzbach

This file is part of dryjq.

dryjq is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

dryjq is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import argparse
import logging

import sys

try:
    import fcntl
except ModuleNotFoundError:
    ...
#

from typing import IO, Type

import yaml

import dryjq


#
# Constants
#


RETURNCODE_OK = 0
RETURNCODE_ERROR = 1


#
# Functions
#


def lock_file(file_handle: IO, operation: int = 0) -> None:
    """Lock the given file"""
    try:
        locking_function = fcntl.flock
    except NameError:
        return
    #
    locking_function(file_handle, operation)


def execute_query(
    arguments: argparse.Namespace, file_handler: dryjq.FileReader
) -> int:
    """Execute the query, write output and return the returncode"""
    try:
        file_handler.execute_single_query(arguments.query)
        file_handler.write_output(
            output_format=arguments.output_format,
            indent=arguments.output_indent,
            sort_keys=arguments.output_sort_keys,
        )
    except (TypeError, ValueError) as error:
        logging.error(error)
        return RETURNCODE_ERROR
    except yaml.YAMLError as error:
        try:
            mark = getattr(error, "problem_mark")
        except AttributeError:
            pass
        else:
            logging.error(
                "Parser error at line %s, column %s:",
                mark.line + 1,
                mark.column + 1,
            )
        #
        logging.error(error)
        return RETURNCODE_ERROR
    #
    return RETURNCODE_OK


def handle_io(arguments: argparse.Namespace) -> int:
    """Handle input and output, the return the returncode"""
    if arguments.input_file is None:
        if arguments.modify_in_place:
            logging.warning("Cannot modify <stdin> in place")
        #
        return execute_query(arguments, dryjq.FileReader(sys.stdin))
    #
    exclusive_lock: int = 0
    shared_lock: int = 0
    unlock_operation: int = 0
    try:
        exclusive_lock = fcntl.LOCK_EX
    except NameError:
        logging.warning(
            "File locking/unlocking using fcntl not avaliable on %s.",
            sys.platform,
        )
    else:
        shared_lock = fcntl.LOCK_SH
        unlock_operation = fcntl.LOCK_UN
    #
    lock_operation = shared_lock
    handler_class: Type[dryjq.FileReader] = dryjq.FileReader
    open_mode = "r"
    if arguments.modify_in_place:
        lock_operation = exclusive_lock
        handler_class = dryjq.FileWriter
        open_mode = "r+"
    #
    with open(
        arguments.input_file, mode=open_mode, encoding="utf-8"
    ) as input_file:
        lock_file(input_file, lock_operation)
        returncode = execute_query(arguments, handler_class(input_file))
        lock_file(input_file, unlock_operation)
    #
    return returncode


def main() -> int:
    """Parse command line arguments and execute the matching function"""
    main_parser = argparse.ArgumentParser(
        prog="dryjq",
        description="Drastically Reduced YAML / JSON Query",
    )
    main_parser.set_defaults(
        loglevel=logging.INFO, query=".", indent=dryjq.DEFAULT_INDENT
    )
    main_parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=logging.DEBUG,
        dest="loglevel",
        help="output all messages including debug level",
    )
    main_parser.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        const=logging.WARNING,
        dest="loglevel",
        help="limit message output to warnings and errors",
    )
    main_parser.add_argument(
        "--version",
        action="store_true",
        help="print version and exit",
    )
    main_parser.add_argument(
        "--modify-in-place",
        action="store_true",
        help="Modify the input file in place instead of writing"
        " the result to standard output. NOT AVAILABLE YET.",
    )
    output_group = main_parser.add_argument_group(
        "Output options", "Options controlling how output is formatted"
    )
    output_group.add_argument(
        "-of",
        "--output-format",
        type=str.upper,
        choices=dryjq.SUPPORTED_FORMATS,
        help="File format."
        "If not provided, the detected input format is used.",
    )
    output_group.add_argument(
        "-oi",
        "--output-indent",
        choices=(2, 4, 8),
        type=int,
        help="Indentation depth of blocks, in spaces (default: %(default)s)",
    )
    output_group.add_argument(
        "-osk",
        "--output-sort-keys",
        action="store_true",
        help="Sort mapping keys."
        " By default, mapping keys are left in input order.",
    )
    main_parser.add_argument(
        "query",
        nargs="?",
        help="The query (simplest form of yq/jq syntax,"
        " default is %(default)s).",
    )
    main_parser.add_argument(
        "input_file",
        nargs="?",
        help="The input file name."
        " If not provided, data will be read from standard input.",
    )
    arguments = main_parser.parse_args()
    if arguments.version:
        print(dryjq.__version__)
        return RETURNCODE_OK
    #
    logging.basicConfig(
        format="%(levelname)-8s\u2551 %(message)s", level=arguments.loglevel
    )
    # XXX: fuse
    if arguments.modify_in_place:
        logging.warning("Early development fuse: deactivating --in-place")
        arguments.modify_in_place = False
    #
    return handle_io(arguments)


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
