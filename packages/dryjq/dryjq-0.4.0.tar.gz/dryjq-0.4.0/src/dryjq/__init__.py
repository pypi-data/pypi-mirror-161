# -*- coding: utf-8 -*-

"""

dryjq

Core module

Copyright (C) 2022 Rainer Schwarzbach

This file is part of dryjq.

dryjq is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

dryjq is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""

__version__ = "0.4.0"


import collections
import copy
import json
import logging
import sys

from typing import Any, List, IO, Optional, Tuple

import yaml


DEFAULT_INDENT = 2

FORMAT_JSON = "JSON"
FORMAT_YAML = "YAML"

SUPPORTED_FORMATS = (FORMAT_JSON, FORMAT_YAML)


class PathComponent:

    """single index component of a DataStructureAddress"""

    def __init__(self, index: Any, in_subscript: bool = False) -> None:
        """Initialize with the index"""
        self.__index = index
        self.__allow_lists = in_subscript
        if not in_subscript:
            self.__reason = "not in subscript"
        if not isinstance(index, int):
            self.__allow_lists = False
            self.__reason = "not a valid list index"
        #

    def get_value(self, data_structure: Any) -> Any:
        """Get the value from data_structure[self.__index]"""
        if not isinstance(data_structure, (list, dict)):
            raise TypeError(
                f"Index {self.__index!r} is not suitable for scalar value"
                f" {data_structure!r}!"
            )
        #
        if isinstance(data_structure, list) and not self.__allow_lists:
            raise TypeError(
                f"Index {self.__index!r} is not suitable for lists"
                f" ({self.__reason})!"
            )
        #
        try:
            value = data_structure[self.__index]
        except (IndexError, KeyError) as error:
            raise ValueError(
                f"Index {self.__index!r} not found in {data_structure!r}!"
            ) from error
        #
        logging.debug("Value at %r is %r", self.__index, value)
        return value

    def replace_value(self, data_structure: Any, new_value: Any) -> None:
        """Modify data_structure:
        replace the value at the existing index by new_value
        """
        # Ensure the index aready exists
        self.get_value(data_structure)
        data_structure[self.__index] = new_value

    def __repr__(self) -> str:
        """Return a representation"""
        if self.__allow_lists:
            purpose = "for maps and lists"
        else:
            purpose = "for maps only"
        #
        return f"<Index {self.__index!r} ({purpose})>"


class DataStructureAddress:

    """Address in data structures,
    a sequence of PathComponent instances.
    """

    def __init__(self, *components: Any) -> None:
        """Initialize the internal components"""
        self.__complete_path = components

    def get_value(self, data_structure: Any) -> Any:
        """Get a value or substructure from data_structure
        using self.__complete_path
        """
        current_value = data_structure
        for element in self.__complete_path:
            current_value = element.get_value(current_value)
        #
        return current_value

    def replace_value(self, data_structure: Any, new_value: Any) -> Any:
        """Replace a value in the data structure,
        and return a copy with the replaced value
        """
        if not self.__complete_path:
            return new_value
        #
        ds_copy = copy.deepcopy(data_structure)
        current_value = ds_copy
        for element in self.__complete_path[:-1]:
            current_value = element.get_value(current_value)
        #
        last_element = self.__complete_path[-1]
        last_element.replace_value(current_value, new_value)
        return ds_copy


class QueryParser:

    """Parse a query string"""

    token_start = "QUERY START"
    token_end = "QUERY END"
    token_literal = "LITERAL"
    token_separator = "SEPARATOR"
    token_subscript_open = "SUBSCRIPT OPENING"
    token_subscript_close = "SUBSCRIPT CLOSING"
    token_spacing = "SPACING"
    token_assignment = "ASSIGNMENT"

    separator = "."
    quotes = ("'", '"')
    spacing = (" ", "\t", "\r", "\n")
    subscript_open = "["
    subscript_close = "]"
    assignment = "="

    @classmethod
    def tokenize(cls, original_query: str) -> List:
        """Tokenize an original query"""
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
        query_characters = collections.deque(original_query)
        in_subscript = False
        in_quoted = None
        current_literal: List[str] = []
        last_token = (cls.token_start, cls.token_start)
        tokens = [last_token]
        position = 0
        while query_characters:
            position = position + 1
            character = query_characters.popleft()
            if in_quoted:
                current_literal.append(character)
                if character == in_quoted:
                    last_token = (cls.token_literal, "".join(current_literal))
                    current_literal.clear()
                    tokens.append(last_token)
                    in_quoted = None
                #
                continue
            #
            if in_subscript:
                if character in cls.spacing:
                    last_token = (cls.token_spacing, character)
                    tokens.append(last_token)
                    continue
                #
                if character in cls.subscript_close:
                    if current_literal:
                        tokens.append(
                            (cls.token_literal, "".join(current_literal))
                        )
                        current_literal.clear()
                    #
                    last_token = (cls.token_subscript_close, character)
                    tokens.append(last_token)
                    in_subscript = False
                    continue
                #
                if character in cls.subscript_open:
                    logging.warning(
                        "Possible error: found unexpected %s character %r"
                        " in subscript",
                        cls.token_subscript_open,
                        character,
                    )
                #
            elif character in cls.subscript_open:
                # close current literal
                if current_literal:
                    tokens.append(
                        (cls.token_literal, "".join(current_literal))
                    )
                    current_literal.clear()
                #
                last_token = (cls.token_subscript_open, character)
                tokens.append(last_token)
                in_subscript = True
                continue
            #
            if character in cls.separator:
                # close current literal
                if current_literal:
                    tokens.append(
                        (cls.token_literal, "".join(current_literal))
                    )
                    current_literal.clear()
                #
                last_token = (cls.token_separator, character)
                tokens.append(last_token)
                continue
            #
            if character in cls.quotes:
                if not current_literal:
                    # Ignore quotes inside literals
                    in_quoted = character
                #
                current_literal.append(character)
                in_quoted = character
                continue
            #
            if character in cls.spacing:
                # close current literal
                if current_literal:
                    tokens.append(
                        (cls.token_literal, "".join(current_literal))
                    )
                    current_literal.clear()
                #
                last_token = (cls.token_spacing, character)
                tokens.append(last_token)
                continue
            #
            if character in cls.assignment:
                # close current literal
                if current_literal:
                    tokens.append(
                        (cls.token_literal, "".join(current_literal))
                    )
                    current_literal.clear()
                #
                last_token = (cls.token_assignment, character)
                tokens.append(last_token)
                break
            #
            # append all other characters
            # to the current literal
            current_literal.append(character)
        #
        if current_literal:
            last_token = (cls.token_literal, "".join(current_literal))
            current_literal.clear()
            tokens.append(last_token)
        #
        if last_token[0] == cls.token_assignment:
            # append the rest as a literal
            tokens.append((cls.token_literal, "".join(query_characters)))
        #
        tokens.append((cls.token_end, cls.token_end))
        if in_quoted:
            raise ValueError(f"Unclosed quote ({in_quoted})!")
        #
        if in_subscript:
            raise ValueError(f"Unclosed subscript ({cls.subscript_open})!")
        #
        return tokens
        #

    @classmethod
    def get_path_component(
        cls, literals: List[str], in_subscript: bool = False
    ) -> PathComponent:
        """Return a path component from the literals"""
        if not literals:
            raise ValueError("Empty path component")
        #
        if len(literals) > 1:
            component_index = "".join(
                yaml.safe_load(item) for item in literals
            )
        else:
            component_index = yaml.safe_load(literals[0])
        #
        return PathComponent(component_index, in_subscript=in_subscript)

    @classmethod
    def parse_query(
        cls, query: str
    ) -> Tuple[DataStructureAddress, Optional[str]]:
        """Parse the given query and return a tuple
        containing a data structure address
        and - optionally - a new value
        """
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
        tokens = collections.deque(cls.tokenize(query))
        logging.debug("Found tokens in query:")
        for (token_type, token_value) in tokens:
            logging.debug("%-20s -> %r", token_type, token_value)
        #
        started = False
        in_subscript = False
        replacement = None
        path_components = []
        current_literal: List[str] = []
        while tokens:
            (token_type, token_value) = tokens.popleft()
            if not started:
                if token_type in (cls.token_start, cls.token_spacing):
                    continue
                #
                if token_type == cls.token_separator:
                    started = True
                    continue
                #
                raise ValueError(
                    f"The query must start with a {cls.separator!r}!"
                )
            #
            if token_type == cls.token_end:
                if current_literal:
                    path_components.append(
                        cls.get_path_component(
                            current_literal, in_subscript=in_subscript
                        )
                    )
                    current_literal.clear()
                #
                break
            #
            if token_type in cls.token_literal:
                current_literal.append(token_value)
            elif token_type == cls.token_separator:
                if current_literal:
                    path_components.append(
                        cls.get_path_component(
                            current_literal, in_subscript=in_subscript
                        )
                    )
                    current_literal.clear()
                #
            elif token_type == cls.token_subscript_open:
                if current_literal:
                    path_components.append(
                        cls.get_path_component(
                            current_literal, in_subscript=in_subscript
                        )
                    )
                    current_literal.clear()
                #
                in_subscript = True
            elif token_type == cls.token_subscript_close:
                if current_literal:
                    path_components.append(
                        cls.get_path_component(
                            current_literal, in_subscript=in_subscript
                        )
                    )
                    current_literal.clear()
                #
                in_subscript = False
            elif token_type == cls.token_assignment:
                if current_literal:
                    path_components.append(
                        cls.get_path_component(
                            current_literal, in_subscript=in_subscript
                        )
                    )
                    current_literal.clear()
                #
                (token_type, token_value) = tokens.popleft()
                if token_type == cls.token_end:
                    logging.warning("Assuming empty assignment value")
                    replacement = ""
                elif token_type == cls.token_literal:
                    replacement = token_value
                else:
                    raise ValueError(
                        f"Unexpected {token_type} token {token_value!r}!"
                    )
                #
                break
            #
        #
        logging.debug("Path components: %r", path_components)
        return (DataStructureAddress(*path_components), replacement)


class DataHandler:

    """Data structure handler"""

    def __init__(self, data: Any) -> None:
        """Initialize the handler with data"""
        self.filtered_data = data
        self.updated_data = False

    def dump_data(
        self,
        output_format: str = FORMAT_YAML,
        indent: int = DEFAULT_INDENT,
        sort_keys: bool = False,
    ) -> str:
        """Return a dump of self.data"""
        if output_format == FORMAT_JSON:
            return json.dumps(
                self.filtered_data,
                indent=indent,
                ensure_ascii=True,
                sort_keys=sort_keys,
            )
        #
        output = yaml.safe_dump(
            self.filtered_data,
            allow_unicode=True,
            default_flow_style=False,
            indent=indent,
            sort_keys=sort_keys,
            explicit_end=False,
        )
        if isinstance(self.filtered_data, (dict, list)):
            return output
        #
        if output.rstrip().endswith("\n..."):
            output = output.rstrip()[:-3]
        #
        return output

    def execute_single_query(
        self,
        data_path: DataStructureAddress,
        replacement_value: Optional[str] = None,
    ) -> None:
        """Execute the provided query, modifying self.data"""
        logging.debug("Filtered data before executing the query:")
        logging.debug("%r", self.filtered_data)
        if replacement_value is None:
            self.filtered_data = data_path.get_value(self.filtered_data)
        else:
            self.filtered_data = data_path.replace_value(
                self.filtered_data, yaml.safe_load(replacement_value.strip())
            )
            self.updated_data = True
        #
        logging.debug("Filtered data after executing the query:")
        logging.debug("%r", self.filtered_data)


class FileReader:

    """YAML or JSON file reader"""

    def __init__(self, file_handler: IO) -> None:
        """Initialize the reader"""
        self.__file_handler = file_handler
        if self.file_handler != sys.stdin:
            self.file_handler.seek(0)
        #
        contents = self.file_handler.read()
        try:
            self.data_handler = DataHandler(json.loads(contents))
        except json.JSONDecodeError:
            self.data_handler = DataHandler(yaml.safe_load(contents))
            self.__input_format = FORMAT_YAML
        else:
            self.__input_format = FORMAT_JSON
        #
        self.original_contents = contents

    @property
    def file_handler(self) -> IO:
        """Return the file handler"""
        return self.__file_handler

    def get_data_dump(self, **output_options: Any) -> str:
        """Get a dump of currently filtered data
        from the data handler
        """
        if not output_options.get("output_format"):
            output_options["output_format"] = self.__input_format
        #
        return self.data_handler.dump_data(**output_options)

    def write_output(self, **output_options: Any) -> None:
        """Write output to stdout"""
        data_dump = self.get_data_dump(**output_options).rstrip()
        sys.stdout.write(f"{data_dump}\n")


class FileWriter(FileReader):

    """File writer
    No locking done here, the caller is responsible for that.
    """

    def write_output(self, **output_options: Any) -> None:
        """Write output to self.file_handler"""
        data_dump = self.get_data_dump(**output_options)
        if data_dump == self.original_contents:
            logging.warning("Not writing unchanged file contents")
            return
        #
        if not self.data_handler.updated_data:
            logging.warning("No data replaced.")
            logging.warning(
                "Query results are displayed below"
                " instead of updating the file:"
            )
            sys.stdout.write(f"{data_dump.rstrip()}\n")
            return
        #
        self.file_handler.seek(0)
        self.file_handler.truncate(0)
        self.file_handler.write(data_dump)


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
