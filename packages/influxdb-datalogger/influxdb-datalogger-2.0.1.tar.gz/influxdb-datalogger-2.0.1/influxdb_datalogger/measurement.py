from typing import Union, Iterable

from .field import Field, FieldMap
from .tag import Tag, TagMap


class Measurement(str):
    def __new__(cls, measurement_name: str,
                *fields_and_tags: Union[Tag, Field], optional_tags: Iterable[Tag] = None):
        """
        Define a measurement to be used for logging data.

        Args:
            measurement_name: The name of the measurement.
            fields: The fields to be used for the measurement.
            *tags: An arbitrary tuple of arbitrary tags to be used for tagging the data.
            optional_tags: Tags that are optional and which must not be configured.
        """

        obj = super().__new__(cls, measurement_name)
        obj.key_name = measurement_name
        obj.fields = set()
        obj.tags = set()
        for _obj in fields_and_tags:
            if isinstance(_obj, Tag):
                obj.tags.add(_obj)
            elif isinstance(_obj, Field):
                obj.fields.add(_obj)
            else:
                raise TypeError(f"Unsupported type for field/tag: {type(obj)}")

        if optional_tags:
            for tag in optional_tags:
                assert isinstance(tag, Tag), f"Unsupported type for lenient tag: {type(tag)}. Must be type {Tag}"
                obj.tags.add(tag)

        obj.optional_tags = optional_tags if optional_tags else set()
        return obj

    def get_predefined_tags(self) -> TagMap:
        """Run 'func' for all tags that have the value defined already."""
        fm = TagMap()
        for tag in self.tags:
            assert isinstance(tag, Tag), f"Tag {tag} is of type {type(tag)}, not {Tag}"
            if tag.func is not None:
                fm[tag] = tag.func(*tag.args_func)
        return fm

    def get_defaulted_tags(self) -> TagMap:
        """Get all tags with defaults defined"""
        tm = TagMap()
        for tag in self.tags:
            assert isinstance(tag, Tag), f"Tag {tag} is of type {type(tag)}, not {Tag}"
            if tag.default is not None:
                tm[tag] = tag.default
        return tm

    def get_predefined_fields(self) -> FieldMap:
        """Run 'func' for all fields that func set."""
        fm = FieldMap()
        for field in self.fields:
            assert isinstance(field, Field), f"Field {field} is of type {type(field)}, not {Field}"
            if field.func is not None:
                fm[field] = field.func(*field.args_func)
        return fm

    def get_default_fields(self) -> FieldMap:
        """Get all tags with defaults defined"""
        fm = FieldMap()
        for field in self.fields:
            assert isinstance(field, Field), f"Field {field} is of type {type(field)}, not {Field}"
            if field.default is not None:
                fm[field] = field.default
        return fm
