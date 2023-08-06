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

__version__ = "0.1.1"


import copy
import logging
import sys

from typing import Any, List, IO

import yaml


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


class BaseYAMLHandler:

    """YAML (file) handler base class"""

    def __init__(self, file_handler: IO) -> None:
        """Initialize the reader"""
        self.__file_handler = file_handler
        if self.file_handler != sys.stdin:
            self.file_handler.seek(0)
        #
        self.data = yaml.safe_load(self.file_handler.read())

    @property
    def file_handler(self) -> IO:
        """Return the file handler"""
        return self.__file_handler

    def load_data(self) -> None:
        """XXX: Load data from the file into self.data"""
        self.file_handler.seek(0)
        self.data = yaml.safe_load(self.file_handler.read())

    def dump_data(
        self,
        allow_unicode: bool = True,
        default_flow_style: bool = False,
        sort_keys: bool = False,
    ) -> str:
        """Return a YAML dump of self.data"""
        output = yaml.dump(
            self.data,
            allow_unicode=allow_unicode,
            default_flow_style=default_flow_style,
            sort_keys=sort_keys,
            explicit_end=False,
        )
        if isinstance(self.data, (dict, list)):
            return output
        #
        if output.rstrip().endswith("\n..."):
            output = output.rstrip()[:-3]
        #
        return output

    def execute_single_query(self, query: str) -> None:
        """Execute the provided query, modifying self.data"""
        source_data = copy.deepcopy(self.data)
        query_obj = Query.from_string(query)
        self.data = query_obj.execute_on(source_data)

    def write_output(self) -> None:
        """Write output (abstract method)"""
        raise NotImplementedError


class YAMLReader(BaseYAMLHandler):

    """YAML reader"""

    def write_output(self) -> None:
        """Write output to stdout"""
        sys.stdout.write(f"{self.dump_data().rstrip()}\n")


class YAMLWriter(BaseYAMLHandler):

    """YAML file writer
    No locking done here, the caller is responsible for that.
    """

    def write_output(self) -> None:
        """Write output to self.file_handler"""
        self.file_handler.seek(0)
        self.file_handler.write(self.dump_data())


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
