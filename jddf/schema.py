from typing import Any
from enum import Enum, auto


class Form(Enum):
    EMPTY = auto()
    REF = auto()
    TYPE = auto()
    ENUM = auto()
    ELEMENTS = auto()
    PROPERTIES = auto()
    VALUES = auto()
    DISCRIMINATOR = auto()


class Schema:
    TYPE_VALUES = [
        'boolean',
        'int8',
        'uint8',
        'int16',
        'uint16',
        'int32',
        'uint32',
        'float32',
        'float64',
        'string',
        'timestamp',
    ]

    def __init__(self, **kwargs):
        self.definitions = kwargs.get('definitions')
        self.ref = kwargs.get('ref')
        self.type = kwargs.get('type')
        self.enum = kwargs.get('enum')
        self.elements = kwargs.get('elements')
        self.properties = kwargs.get('properties')
        self.optional_properties = kwargs.get('optional_properties')
        self.additional_properties = kwargs.get('additional_properties')
        self.values = kwargs.get('values')
        self.discriminator = kwargs.get('discriminator')

    @staticmethod
    def from_json(value: Any) -> 'Schema':
        schema = Schema()

        if type(value) is not dict:
            raise TypeError('schema not dict')

        definitions = value.get('definitions')
        if definitions is not None:
            if type(definitions) is not dict:
                raise TypeError('definitions not dict')

            schema.definitions = {}
            for key, sub_value in definitions.items():
                schema.definitions[key] = Schema.from_json(sub_value)

        ref = value.get('ref')
        if ref is not None:
            if type(ref) is not str:
                raise TypeError('ref not str')

            schema.ref = ref

        typ = value.get('type')
        if typ is not None:
            if typ not in Schema.TYPE_VALUES:
                raise TypeError('type not one of Schema.TYPE_VALUES')

            schema.type = typ

        enum = value.get('enum')
        if enum is not None:
            if type(enum) is not list:
                raise TypeError('enum not list')

            if len(enum) == 0:
                raise TypeError('enum empty')

            for elem in enum:
                if type(elem) is not str:
                    raise TypeError('enum element not str')

            schema.enum = set(enum)

            if len(schema.enum) != len(enum):
                raise TypeError('enum contains duplicates')

        elements = value.get('elements')
        if elements is not None:
            schema.elements = Schema.from_json(elements)

        properties = value.get('properties')
        if properties is not None:
            if type(properties) is not dict:
                raise TypeError('properties not dict')

            schema.properties = {}
            for key, sub_value in properties.items():
                schema.properties[key] = Schema.from_json(sub_value)

        optional_properties = value.get('optionalProperties')
        if optional_properties is not None:
            if type(optional_properties) is not dict:
                raise TypeError('optionalProperties not dict')

            schema.optional_properties = {}
            for key, sub_value in optional_properties.items():
                schema.optional_properties[key] = Schema.from_json(sub_value)

        additional_properties = value.get('additionalProperties')
        if additional_properties is not None:
            if type(additional_properties) is not bool:
                raise TypeError('additionalProperties not bool')

            schema.additional_properties = additional_properties

        values = value.get('values')
        if values is not None:
            schema.values = Schema.from_json(values)

        discriminator = value.get('discriminator')
        if discriminator is not None:
            schema.discriminator = Discriminator.from_json(discriminator)

        return schema

    def verify(self, root=None) -> 'Schema':
        if root is None:
            root = self

        if self.definitions:
            for value in self.definitions.values():
                value.verify(root)

        empty = True

        if self.ref is not None:
            empty = False

            if self.ref not in root.definitions:
                raise TypeError('ref to nonexistent definition')

        if self.type is not None:
            if not empty:
                raise TypeError('invalid form')

            empty = False

        if self.enum is not None:
            if not empty:
                raise TypeError('invalid form')

            empty = False

        if self.elements is not None:
            if not empty:
                raise TypeError('invalid form')

            empty = False

            self.elements.verify(root)

        if self.properties is not None or self.optional_properties is not None:
            if not empty:
                raise TypeError('invalid form')

            empty = False

            if self.properties:
                for value in self.properties.values():
                    value.verify(root)

            if self.optional_properties:
                for value in self.optional_properties.values():
                    value.verify(root)

        if self.properties is not None and self.optional_properties is not None:
            properties = set(self.properties.keys())
            optional_properties = set(self.optional_properties.keys())
            if properties.intersection(set(optional_properties)):
                raise TypeError('properties and optionalProperties share key')

        if self.values is not None:
            if not empty:
                raise TypeError('invalid form')

            empty = False

            self.values.verify(root)

        if self.discriminator is not None:
            if not empty:
                raise TypeError('invalid form')

            empty = False

            for value in self.discriminator.mapping.values():
                value.verify(root)

                if value.form() != Form.PROPERTIES:
                    raise TypeError(
                        'discriminator mapping value not of properties form')

                tag = self.discriminator.tag
                in_properties = value.properties and tag in value.properties
                in_optional_properties = value.optional_properties and tag in value.optional_properties

                if in_properties or in_optional_properties:
                    raise TypeError(
                        'discriminator tag repeated in mapping value')

        return self

    def form(self) -> Form:
        if self.ref is not None:
            return Form.REF
        if self.type is not None:
            return Form.TYPE
        if self.enum is not None:
            return Form.ENUM
        if self.elements is not None:
            return Form.ELEMENTS
        if self.properties is not None or self.optional_properties is not None:
            return Form.PROPERTIES
        if self.values is not None:
            return Form.VALUES
        if self.discriminator is not None:
            return Form.DISCRIMINATOR
        return Form.EMPTY


class Discriminator:
    def __init__(self, **kwargs):
        self.tag = kwargs.get('tag')
        self.mapping = kwargs.get('mapping')

    @staticmethod
    def from_json(value: Any) -> 'Discriminator':
        discriminator = Discriminator()

        if type(value) is not dict:
            raise TypeError('discriminator not dict')

        tag = value.get('tag')
        if type(tag) is not str:
            raise TypeError('tag not str')

        discriminator.tag = tag

        mapping = value.get('mapping')
        if type(mapping) is not dict:
            raise TypeError('mapping not dict')

        discriminator.mapping = {}
        for key, sub_value in mapping.items():
            discriminator.mapping[key] = Schema.from_json(sub_value)

        return discriminator
