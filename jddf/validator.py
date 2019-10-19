from jddf.schema import Form, Schema
from typing import Any, List, Optional
from strict_rfc3339 import validate_rfc3339


class ValidationError:
    def __init__(self, instance_path: List[str], schema_path: List[str]):
        self.instance_path = instance_path
        self.schema_path = schema_path

    def __eq__(self, value):
        return self.schema_path == value.schema_path and self.instance_path == value.instance_path

    def __repr__(self):
        return str(self.__dict__)


class Validator:
    class _VM:
        def __init__(self, schema: Schema, max_depth: int, max_errors: int):
            self.root = schema
            self.max_depth = max_depth
            self.max_errors = max_errors
            self.schema_tokens = [[]]
            self.instance_tokens = []
            self.errors = []

        def validate(self, schema: Schema, instance: Any, parent_tag: Optional[str] = None):
            if schema.form() == Form.REF:
                self.schema_tokens.append(["definitions", schema.ref])
                self.validate(self.root.definitions[schema.ref], instance)
                self.schema_tokens.pop()
            elif schema.form() == Form.TYPE:
                self.push_schema_token("type")
                if schema.type == "boolean":
                    if type(instance) is not bool:
                        self.push_error()
                elif schema.type == "float32" or schema.type == "float64":
                    if type(instance) is not float and type(instance) is not int:
                        self.push_error()
                elif schema.type == "int8":
                    self.check_int(-128, 127, instance)
                elif schema.type == "uint8":
                    self.check_int(0, 255, instance)
                elif schema.type == "int16":
                    self.check_int(-32768, 32767, instance)
                elif schema.type == "uint16":
                    self.check_int(0, 65535, instance)
                elif schema.type == "int32":
                    self.check_int(-2147483648, 2147483647, instance)
                elif schema.type == "uint32":
                    self.check_int(0, 4294967295, instance)
                elif schema.type == "string":
                    if type(instance) is not str:
                        self.push_error()
                elif schema.type == "timestamp":
                    if type(instance) is not str or not validate_rfc3339(instance):
                        self.push_error()
                self.pop_schema_token()
            elif schema.form() == Form.ENUM:
                self.push_schema_token("enum")
                if instance not in schema.enum:
                    self.push_error()
                self.pop_schema_token()
            elif schema.form() == Form.ELEMENTS:
                self.push_schema_token("elements")
                if type(instance) is list:
                    for index, sub_instance in enumerate(instance):
                        self.push_instance_token(str(index))
                        self.validate(schema.elements, sub_instance)
                        self.pop_instance_token()
                else:
                    self.push_error()
                self.pop_schema_token()
            elif schema.form() == Form.PROPERTIES:
                if type(instance) is dict:
                    if schema.properties:
                        self.push_schema_token("properties")
                        for key, sub_schema in schema.properties.items():
                            self.push_schema_token(key)

                            if key in instance:
                                self.push_instance_token(key)
                                self.validate(sub_schema, instance[key])
                                self.pop_instance_token()
                            else:
                                self.push_error()

                            self.pop_schema_token()
                        self.pop_schema_token()

                    if schema.optional_properties:
                        self.push_schema_token("optionalProperties")
                        for key, sub_schema in schema.optional_properties.items():
                            self.push_schema_token(key)

                            if key in instance:
                                self.push_instance_token(key)
                                self.validate(sub_schema, instance[key])
                                self.pop_instance_token()

                            self.pop_schema_token()
                        self.pop_schema_token()

                    if not schema.additional_properties:
                        for key in instance.keys():
                            in_properties = schema.properties and key in schema.properties
                            in_optional_properties = schema.optional_properties and key in schema.optional_properties
                            is_parent_tag = key == parent_tag

                            if not in_properties and not in_optional_properties and not is_parent_tag:
                                self.push_instance_token(key)
                                self.push_error()
                                self.pop_instance_token()
                else:
                    if schema.properties is not None:
                        self.push_schema_token("properties")
                    else:
                        self.push_schema_token("optionalProperties")

                    self.push_error()
                    self.pop_schema_token()
            elif schema.form() == Form.VALUES:
                self.push_schema_token("values")
                if type(instance) is dict:
                    for key, value in instance.items():
                        self.push_instance_token(key)
                        self.validate(schema.values, value)
                        self.pop_instance_token()
                else:
                    self.push_error()
                self.pop_schema_token()
            elif schema.form() == Form.DISCRIMINATOR:
                self.push_schema_token("discriminator")
                if type(instance) is dict:
                    if schema.discriminator.tag in instance:
                        if type(instance[schema.discriminator.tag]) is str:
                            self.push_schema_token("mapping")

                            if instance[schema.discriminator.tag] in schema.discriminator.mapping:
                                self.push_schema_token(
                                    instance[schema.discriminator.tag])
                                self.validate(
                                    schema.discriminator.mapping[instance[schema.discriminator.tag]], instance, schema.discriminator.tag)
                                self.pop_schema_token()
                            else:
                                self.push_instance_token(
                                    schema.discriminator.tag)
                                self.push_error()
                                self.pop_instance_token()

                            self.pop_schema_token()
                        else:
                            self.push_schema_token("tag")
                            self.push_instance_token(schema.discriminator.tag)
                            self.push_error()
                            self.pop_instance_token()
                            self.pop_schema_token()
                    else:
                        self.push_schema_token("tag")
                        self.push_error()
                        self.pop_schema_token()
                else:
                    self.push_error()
                self.pop_schema_token()

        def check_int(self, min, max, instance):
            if type(instance) is int or type(instance) is float:
                if int(instance) != instance or instance < min or instance > max:
                    self.push_error()
            else:
                self.push_error()

        def push_schema_token(self, token: str):
            self.schema_tokens[-1].append(token)

        def pop_schema_token(self):
            self.schema_tokens[-1].pop()

        def push_instance_token(self, token: str):
            self.instance_tokens.append(token)

        def pop_instance_token(self):
            self.instance_tokens.pop()

        def push_error(self):
            self.errors.append(ValidationError(
                self.instance_tokens.copy(),
                self.schema_tokens[-1].copy()))

    def __init__(self, **kwargs):
        self.max_depth = kwargs.get('max_depth', 0)
        self.max_errors = kwargs.get('max_errors', 0)

    def validate(self, schema: Schema, instance: Any) -> List[ValidationError]:
        vm = Validator._VM(schema, self.max_depth, self.max_errors)
        vm.validate(schema, instance)
        return vm.errors
