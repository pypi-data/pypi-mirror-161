from __future__ import annotations

from typing import Callable

from .datalogger_map import DataLoggerMap


class Field(str):
    def __new__(cls, field_name: str, *args_func: object, func: Callable = None, default: object = None):
        """
        Define a Field to be used for logging data.

        Args:
            field_name: The name of the field.
            args_func: Optional arguments to pass to func.
        """

        obj = super().__new__(cls, field_name)
        obj.field_name = field_name
        obj.func = func
        obj.default = default

        if not args_func:
            args_func = tuple()
        obj.args_func = args_func
        return obj


class FieldMap(DataLoggerMap):
    @property
    def key_type(self):
        return Field

