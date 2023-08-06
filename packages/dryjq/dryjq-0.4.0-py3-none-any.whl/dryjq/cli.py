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

from typing import Any, IO, List, Optional, Type

import yaml

import dryjq


#
# Constants
#


NO_LOCK_OPERATION = 0

RETURNCODE_OK = 0
RETURNCODE_ERROR = 1


#
# Helper class
#


class FileHelper:

    """File handling helper class"""

    def __init__(
        self,
        file_name: Optional[str],
        modify_in_place: bool = False,
        replace_value_mode: bool = False,
    ) -> None:
        """Determine whether the file should be opened in r
        in r or r+ mode, then return a tuple containing
        the file handler class, the open mode for the file
        and the lock and unlock operation magic numbers
        """
        if file_name is None:
            raise ValueError("No file name supplied!")
        #
        self.file_name = file_name
        exclusive_lock = NO_LOCK_OPERATION
        shared_lock = NO_LOCK_OPERATION
        unlock_operation = NO_LOCK_OPERATION
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
        self.lock_operation = shared_lock
        self.unlock_operation = unlock_operation
        self.handler_class: Type[dryjq.FileReader] = dryjq.FileReader
        self.open_mode = "r"
        if modify_in_place and replace_value_mode:
            self.lock_operation = exclusive_lock
            self.handler_class = dryjq.FileWriter
            self.open_mode = "r+"
        #

    def open(self, encoding: Optional[str] = None) -> IO[Any]:
        """Wrapper around open()"""
        return open(self.file_name, mode=self.open_mode, encoding=encoding)

    @staticmethod
    def execute_lock_op(file_handle: IO, operation: int) -> None:
        """Execute the supplied lock operation"""
        try:
            locking_function = fcntl.flock
        except NameError:
            return
        #
        locking_function(file_handle, operation)

    def lock(self, file_handle: IO) -> None:
        """Lock the file"""
        self.execute_lock_op(file_handle, self.lock_operation)

    def unlock(self, file_handle: IO) -> None:
        """Lock the file"""
        self.execute_lock_op(file_handle, self.unlock_operation)


#
# Functions
#


def execute_query(
    file_handler: dryjq.FileReader,
    data_path: dryjq.DataStructureAddress,
    replacement_value: Optional[str] = None,
    **output_options: Any,
) -> int:
    """Execute the query, write output and return the returncode"""
    try:
        file_handler.data_handler.execute_single_query(
            data_path, replacement_value=replacement_value
        )
        file_handler.write_output(**output_options)
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


def main(args: Optional[List[str]] = None) -> int:
    """Parse command line arguments and execute the matching function"""
    main_parser = argparse.ArgumentParser(
        prog="dryjq",
        description="Drastically Reduced YAML / JSON Query",
    )
    main_parser.set_defaults(
        loglevel=logging.INFO, query=".", output_indent=dryjq.DEFAULT_INDENT
    )
    main_parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=logging.DEBUG,
        dest="loglevel",
        help="Output all messages including debug level",
    )
    main_parser.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        const=logging.ERROR,
        dest="loglevel",
        help="Limit message output to errors",
    )
    main_parser.add_argument(
        "--version",
        action="store_true",
        help="Print version and exit",
    )
    main_parser.add_argument(
        "--modify-in-place",
        action="store_true",
        help="Modify the input file in place instead of writing"
        " the result to standard output.",
    )
    output_group = main_parser.add_argument_group(
        "Output options", "control how output will be formatted"
    )
    output_group.add_argument(
        "-of",
        "--output-format",
        type=str.upper,
        choices=dryjq.SUPPORTED_FORMATS,
        help="File format. By default, the detected input format is used.",
    )
    output_group.add_argument(
        "-oi",
        "--output-indent",
        choices=(2, 4, 8),
        type=int,
        help="Indentation depth of blocks, in spaces (default: %(default)s).",
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
        " default is %(default)r).",
    )
    main_parser.add_argument(
        "input_file",
        nargs="?",
        help="The input file name."
        " By default, data will be read from standard input.",
    )
    arguments = main_parser.parse_args(args)
    if arguments.version:
        print(dryjq.__version__)
        return RETURNCODE_OK
    #
    logging.basicConfig(
        format="%(levelname)-8s\u2551 (%(funcName)s) %(message)s",
        level=arguments.loglevel,
    )
    data_path, replacement_value = dryjq.QueryParser.parse_query(
        arguments.query
    )
    output_options = dict(
        output_format=arguments.output_format,
        indent=arguments.output_indent,
        sort_keys=arguments.output_sort_keys,
    )
    if arguments.input_file is None:
        if arguments.modify_in_place:
            logging.warning("Cannot modify <stdin> in place")
        #
        return execute_query(
            dryjq.FileReader(sys.stdin),
            data_path,
            replacement_value=replacement_value,
            **output_options,
        )
    #
    # handler_class, open_mode, lock_operation, unlock_operation =
    file_helper = FileHelper(
        arguments.input_file,
        modify_in_place=arguments.modify_in_place,
        replace_value_mode=(replacement_value is not None),
    )
    with file_helper.open(encoding="utf-8") as input_file:
        file_helper.lock(input_file)
        returncode = execute_query(
            file_helper.handler_class(input_file),
            data_path,
            replacement_value=replacement_value,
            **output_options,
        )
        file_helper.unlock(input_file)
    #
    return returncode


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
