from file_validator.schema.generator import ValidationMapping, BASE_RULES_MAPPING
from file_validator.exception import (
    EmptySchemaException, SchemaMissingFieldsException, NotDeclaredFieldsException,
    NotDeclaredValidationMappingException, InvalidSchemaException, NotDeclaredUniqueFieldsException
)


class Base:
    accepted_file_types = ["csv", "xlsx"]
    silent_exit_for_empty_schema = True
    silent_exit_for_invalid_schema = True
    silent_exit_for_invalid_file_type = True
    silent_exit_for_invalid_file = True
    silent_exit_for_other_exception = True
    base_schema_fields = {"fields", "validations"}
    config_fields = ["FILE", "ALL"]

    def __init__(self):
        self._schema = []
        self._validation_mapping = ValidationMapping()
        self._fields = []

    def __call__(self, *args, **kwargs):
        schema_type = args[0]
        config_json = args[1]
        self._prepare_schema(schema_type, config_json)

    def schema(self):
        return self._schema

    def validations(self):
        return self._schema

    def fields(self):
        return self._fields

    def _append_rule(self, rule):
        self._schema.append(rule)

    def _prepare_schema(self, schema_type, config_dict):
        if not config_dict:
            if self.silent_exit_for_empty_schema:
                return
            else:
                raise EmptySchemaException("Provided config file seems to be empty. {}" . format(config_dict))
            
        if config_dict.get('invalid', False):
            if self.silent_exit_for_invalid_file:
                return
            else:
                raise InvalidSchemaException("Provided config file seems to be invalid. {}" . format(config_dict))

        missing_fields = self.base_schema_fields.difference(set(config_dict.keys()))
        if missing_fields:
            if self.silent_exit_for_invalid_schema:
                return
            else:
                raise SchemaMissingFieldsException("Provided config file missing fields {}. {}".format(
                    missing_fields, config_dict))

        self._parse_schema(schema_type, config_dict)

    def set_validations_mapping(self, mapping):
        self._validation_mapping.add(mapping)

    def validations_mapping(self):
        if self._validation_mapping.has_mapping_set():
            return self._validation_mapping
        return None

    def _parse_schema(self, schema_type, config):
        all_fields = config.get('fields', [])
        unique_keys = config.get('unique', [])

        self._register_base_validations()
        self.set_fields(all_fields)

        if not self.validations_mapping():
            raise NotDeclaredValidationMappingException("Base Validation Mapping needs to be declared.")

        if not self.fields():
            raise NotDeclaredFieldsException("All fields need to be declared.")

        if not unique_keys:
            raise NotDeclaredUniqueFieldsException("Unique field needs to be declared.")

        self.parse_schema(schema_type, config)

    def parse_schema(self, schema_type, config):
        raise NotImplementedError()

    def set_fields(self, fields):
        self._fields = fields

    def _register_base_validations(self):
        self.set_validations_mapping(BASE_RULES_MAPPING)

    def register_custom_validations(self, maps):
        if not maps:
            raise Exception("Provided empty mapping.")

        self.set_validations_mapping(maps)


class GenericSchema(Base):

    @staticmethod
    def _get_validation_attributes(attrib, validation, cls):
        value = validation.get(attrib, None)
        if not value:
            value = getattr(cls, attrib, None)

        return value

    @staticmethod
    def _get_sub_validation_attributes(attrib, validation, sub_validation, cls):
        value = validation.get(attrib, None)
        if sub_validation.get(attrib, None):
            value = sub_validation.get(attrib, None)
        if not value:
            value = getattr(cls, attrib, None)

        return value

    def parse_schema(self, schema_type, config):
        all_fields = config.get('fields', [])
        validations = config.get('validations', [])
        unique_keys = config.get('unique', [])

        if isinstance(unique_keys, str):
            unique_keys = [unique_keys]

        for validate_key, validation in validations.items():
            validation_class = getattr(self.validations_mapping(), validate_key, None)
            if not validation_class:
                raise NotDeclaredValidationMappingException("Please define rule for '{}'.".format(validate_key))
            allow_multiple_config = validation.get('allow_multiple_config', None)

            if allow_multiple_config and validation.get('configs'):
                for sub_validation in validation.get('configs', {}):
                    for field in sub_validation.get('fields', []):
                        if field in all_fields + self.config_fields:
                            self._create_validation_rule(
                                validation_class, validate_key, field, unique_keys,
                                self._get_sub_validation_attributes('constraint', validation, sub_validation, validation_class),
                                self._get_sub_validation_attributes('message', validation, sub_validation, validation_class),
                                self._get_sub_validation_attributes('tags', validation, sub_validation, validation_class),
                                self._get_sub_validation_attributes('pre-validation', validation, sub_validation, validation_class)
                            )
                continue

            for field in validation.get('fields', []):
                if field in all_fields + self.config_fields:
                    self._create_validation_rule(
                        validation_class, validate_key, field, unique_keys,
                        self._get_validation_attributes('constraint', validation, validation_class),
                        self._get_validation_attributes('message', validation, validation_class),
                        self._get_validation_attributes('tags', validation, validation_class),
                        self._get_validation_attributes('pre-validation', validation, validation_class),
                    )

    def _create_validation_rule(self, validation_class, validate_key, field, unique_key, constraint, message, tags, pre_validation):
        self._append_rule(validation_class(
            validate_key=validate_key,
            attribute=field,
            unique_key=unique_key,
            constraint=constraint,
            message=message,
            tags=tags,
            pre_validation=pre_validation
        ))


class FeatureSchema(GenericSchema):
    map = {}

    def parse_schema(self, schema_type, config, **kwargs):
        self.register_custom_validations(self.map)

        super(FeatureSchema, self).parse_schema(schema_type, config)
