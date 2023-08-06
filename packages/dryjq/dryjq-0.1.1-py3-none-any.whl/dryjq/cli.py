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
    arguments: argparse.Namespace, yaml_handler: dryjq.BaseYAMLHandler
) -> int:
    """Execute the query, write output and return the returncode"""
    try:
        yaml_handler.execute_single_query(arguments.query)
        yaml_handler.write_output()
    except (TypeError, ValueError, dryjq.yaml.parser.ParserError) as error:
        logging.critical(error)
        return RETURNCODE_ERROR
    #
    return RETURNCODE_OK


def handle_io(arguments: argparse.Namespace) -> int:
    """Handle input and output, the return the returncode"""
    if arguments.yaml_file is None:
        if arguments.in_place:
            logging.warning("Cannot modify <stdin> in place")
        #
        return execute_query(arguments, dryjq.YAMLReader(sys.stdin))
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
    handler_class: Type[dryjq.BaseYAMLHandler] = dryjq.YAMLReader
    open_mode = "r"
    if arguments.in_place:
        lock_operation = exclusive_lock
        handler_class = dryjq.YAMLWriter
        open_mode = "r+"
    #
    with open(
        arguments.yaml_file, mode=open_mode, encoding="utf-8"
    ) as yaml_file:
        lock_file(yaml_file, lock_operation)
        returncode = execute_query(arguments, handler_class(yaml_file))
        lock_file(yaml_file, unlock_operation)
    #
    return returncode


def main() -> int:
    """Parse command line arguments and execute the matching function"""
    main_parser = argparse.ArgumentParser(
        prog="dryjq",
        description="Drastically reduced YAML / JSON query",
    )
    main_parser.set_defaults(loglevel=logging.INFO, query=".")
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
        "--in-place",
        action="store_true",
        help="Modify the input file in place. NOT AVAILABLE YET.",
    )
    main_parser.add_argument(
        "query",
        nargs="?",
        help="The query (simplest form of yq/jq syntax, default is '.')",
    )
    main_parser.add_argument(
        "yaml_file",
        nargs="?",
        help="The input file name."
        " If not provided, standard input will be used.",
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
    if arguments.in_place:
        logging.warning("Early development fuse: deactivating --in-place")
        arguments.in_place = False
    #
    return handle_io(arguments)


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
