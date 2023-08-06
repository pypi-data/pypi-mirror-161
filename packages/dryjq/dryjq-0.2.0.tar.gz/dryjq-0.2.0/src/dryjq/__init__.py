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

__version__ = "0.2.0"


import copy
import json
import logging
import sys

from typing import Any, List, IO, Optional

import yaml


DEFAULT_INDENT = 2

FORMAT_JSON = "JSON"
FORMAT_YAML = "YAML"

SUPPORTED_FORMATS = (FORMAT_JSON, FORMAT_YAML)


class BaseQuery:

    """Query base class"""

    def __init__(self, *address_parts: str, value: Any = None) -> None:
        """Store the address parts"""
        self.__address_parts = address_parts
        self.modifies = False
        self.value = value

    def execute_on(self, data: Any) -> Any:
        """Execute the query on data"""
        if not self.__address_parts:
            return data
        #
        current_data = copy.copy(data)
        for part in self.__address_parts:
            addresses = []
            while part.endswith("]"):
                part, sub_part = part[:-1].rsplit("[", 1)
                addresses.append(yaml.safe_load(sub_part))
            #
            if part:
                addresses.append(part)
            #
            for sub_address in reversed(addresses):
                logging.debug("Sub-address: %r", sub_address)
                current_data = copy.copy(current_data[sub_address])
            #
        #
        return current_data


class Query(BaseQuery):

    """Query possibly modifying data"""

    def __init__(self, *address_parts: str, value: Any = None) -> None:
        """Store the address parts"""
        super().__init__(*address_parts, value=value)
        self.modifies = True

    @classmethod
    def from_string(cls, query: str) -> BaseQuery:
        """Constructor method"""
        address: str
        text_value: str
        try:
            address, text_value = query.split("=", 1)
        except ValueError:
            address = query
            value: Any = None
            query_class = BaseQuery
        else:
            value = yaml.safe_load(text_value.strip())
            query_class = cls
        #
        address = address.strip()
        address_parts: List = address.split(".")
        if len(address_parts) < 2 or address_parts[0]:
            raise ValueError("The query must start with a dot.")
        #
        address_parts.pop(0)
        if len(address_parts) == 1 and not address_parts[0]:
            address_parts.pop(0)
        #
        return query_class(*address_parts, value=value)


class DataHandler:

    """Data structure handler"""

    def __init__(self, data: Any) -> None:
        """Initialize the handler with data"""
        self.filtered_data = data

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

    def execute_single_query(self, query: str) -> None:
        """Execute the provided query, modifying self.data"""
        source_data = copy.deepcopy(self.filtered_data)
        query_obj = Query.from_string(query)
        self.filtered_data = query_obj.execute_on(source_data)


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

    def execute_single_query(self, query: str) -> None:
        """Execute the provided query in the data handler"""
        self.data_handler.execute_single_query(query)

    def get_data_dump(
        self,
        output_format: Optional[str] = None,
        indent: int = DEFAULT_INDENT,
        sort_keys: bool = False,
    ) -> str:
        """Get a dump of currently filtered data
        from the data handler
        """
        if output_format is None:
            output_format = self.__input_format
        #
        return self.data_handler.dump_data(
            output_format=output_format,
            indent=indent,
            sort_keys=sort_keys,
        )

    def write_output(
        self,
        output_format: Optional[str] = None,
        indent: int = DEFAULT_INDENT,
        sort_keys: bool = False,
    ) -> None:
        """Write output to stdout"""
        data_dump = self.get_data_dump(
            output_format=output_format,
            indent=indent,
            sort_keys=sort_keys,
        ).rstrip()
        sys.stdout.write(f"{data_dump}\n")


class FileWriter(FileReader):

    """File writer
    No locking done here, the caller is responsible for that.
    """

    def write_output(
        self,
        output_format: Optional[str] = None,
        indent: int = DEFAULT_INDENT,
        sort_keys: bool = False,
    ) -> None:
        """Write output to self.file_handler"""
        data_dump = self.get_data_dump(
            output_format=output_format,
            indent=indent,
            sort_keys=sort_keys,
        )
        if data_dump == self.original_contents:
            logging.warning("Not writing unchanged file contents")
            return
        #
        self.file_handler.seek(0)
        self.file_handler.write(data_dump)


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
