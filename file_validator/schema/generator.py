from file_validator.reader.reader import (
    JSONFileReader, CSV
)
from file_validator.validator.rules import (
    RequiredAttributeValidation, IsNullAttributeValidation, IsDateAttributeValidation, FileNameValidation,
    FileTypeValidation, HeaderValidation, IsStringAttributeValidation, AttributeLengthValidation,
    RegexAttributeValidation, EnumAttributeValidation, DateFormatAttributeValidation, AlphaNumericAttributeValidation,
    IsIntegerAttributeValidation, EmailValidation, PhoneValidation,
)


class ValidationMapping(object):
    def has_mapping_set(self):
        return len(self.__dict__) != 0

    def add(self, mapping):
        for map_key, validation_class in mapping.items():
            self.__setattr__(map_key, validation_class)


# TODO: add base rules to this mapping. Custom rules need to be defined at feature level; not here.
BASE_RULES_MAPPING = {
    "required": RequiredAttributeValidation,
    "check_not_null": IsNullAttributeValidation,
    "check_date": IsDateAttributeValidation,
    "file_name": FileNameValidation,
    "file_type": FileTypeValidation,
    "check_column_headers": HeaderValidation,
    "check_string": IsStringAttributeValidation,
    "check_int": IsIntegerAttributeValidation,
    "attribute_length": AttributeLengthValidation,
    "match_regex": RegexAttributeValidation,
    "match_enum": EnumAttributeValidation,
    "match_date_format": DateFormatAttributeValidation,
    "check_alphanumeric": AlphaNumericAttributeValidation,
    "email": EmailValidation,
    "phone": PhoneValidation,
}


class SchemaFactory:
    def __init__(self):
        self.schema_class = None
        self._schema = None

    def generate(self, *args, **kwargs):
        self._schema = self._get_schema(*args, **kwargs)

    def schema(self):
        return self._schema

    def _get_schema(self, schema_class, schema_type, config_path, file_type=CSV, **kwargs):
        has_read, logs, config = self.read(file_type, config_path)

        if not has_read:
            # Unable to read config file; this will be captured while processing schema; no need to handle here.
            print(config)
            print(logs.serialize())

        schema = schema_class()
        schema(
            schema_type,
            config,
            file_type,
            **kwargs
        )
        return schema

    def read(self, file_type, config_path):
        # check_extn set to False because JSON is not an accepted input data type.
        return JSONFileReader().validate_and_read(config_path, 'json', check_extn=False, as_dict=True, is_config=True)
