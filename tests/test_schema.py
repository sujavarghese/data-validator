import json

from file_validator.exception.exception import (
    EmptySchemaException, SchemaMissingFieldsException, NotDeclaredFieldsException, InvalidSchemaException
)
from file_validator.schema.schema import ValidationMapping, Base as BaseSchema, GenericSchema, FeatureSchema
from file_validator.validator.rules import (
    Base as BaseRules, IsNullAttributeValidation, IsDateAttributeValidation, RequiredAttributeValidation
)
from tests import Base as BaseTest


class ValidationA(BaseRules):
    pass


class ValidationB(BaseRules):
    pass


class SchemaA(BaseSchema):
    def parse_schema(self, schema_type, config):
        pass


class GenericSchemaA(GenericSchema):
    silent_exit_for_empty_schema = False
    silent_exit_for_invalid_schema = False
    silent_exit_for_invalid_file_type = False
    silent_exit_for_invalid_file = False
    silent_exit_for_other_exception = False


class FeatureSchemaA(FeatureSchema):
    pass


class TestValidationMapping(BaseTest):
    def should_verify_mapping(self):
        mapping_inst = ValidationMapping()
        mapping_inst.add({'validation_key_a': ValidationA, 'validation_key_b': ValidationB})
        self.assertTrue(mapping_inst.has_mapping_set())

    def should_report_mapping_not_being_added(self):
        mapping_inst = ValidationMapping()
        self.assertFalse(mapping_inst.has_mapping_set())


class TestBaseSchema(BaseTest):
    def should_confirm_accepted_file_types(self):
        self.assertEqual(["csv", "xlsx"], SchemaA.accepted_file_types)

    def should_confirm_silent_exit_for_schema(self):
        self.assertTrue(SchemaA.silent_exit_for_empty_schema)
        self.assertTrue(SchemaA.silent_exit_for_invalid_file)
        self.assertTrue(SchemaA.silent_exit_for_invalid_file_type)
        self.assertTrue(SchemaA.silent_exit_for_invalid_schema)
        self.assertTrue(SchemaA.silent_exit_for_other_exception)

    def should_confirm_template_fields(self):
        self.assertEqual({"fields", "validations"}, SchemaA.base_schema_fields)
        self.assertEqual(["FILE", "ALL"], SchemaA.config_fields)

    def should_verify_no_mapping_set_initially(self):
        schema = SchemaA()
        self.assertIsNone(schema.validations_mapping())


class TestGenericSchema(BaseTest):
    def should_verify_empty_schema_exception(self):
        prepare_schema = GenericSchemaA()
        config = "{}"
        dummy_schema_type = ""
        self.assertRaises(EmptySchemaException, prepare_schema(dummy_schema_type, config))

    def should_verify_schema_field_missing(self):
        prepare_schema = GenericSchemaA()
        config = json.dumps({"validations": {}})
        dummy_schema_type = ""
        self.assertRaises(SchemaMissingFieldsException, prepare_schema(dummy_schema_type, config))

    def should_verify_schema_empty_columns(self):
        prepare_schema = GenericSchemaA()
        config = json.dumps({"validations": {}, "fields": []})
        dummy_schema_type = ""
        self.assertRaises(NotDeclaredFieldsException, prepare_schema(dummy_schema_type, config))

    def should_verify_(self):
        prepare_schema = GenericSchemaA()
        config = '{"fields": ["test_column_1", "test_column_2"], "validations": {},,,,,,}'
        dummy_schema_type = ""
        self.assertRaises(InvalidSchemaException, prepare_schema(dummy_schema_type, config))

    def should_verify_registered_base_validations(self):
        prepare_schema = GenericSchemaA()
        config = json.dumps({"validations": {}, "fields": ["test_column_1", "test_column_2"]})
        dummy_schema_type = ""
        prepare_schema(dummy_schema_type, config)
        mapping_obj = prepare_schema.validations_mapping()
        self.assertDictEqual({
            "required": RequiredAttributeValidation,
            "check_not_null": IsNullAttributeValidation,
            "check_date": IsDateAttributeValidation,
        }, mapping_obj.__dict__)

    def should_verify_registered_fields(self):
        prepare_schema = GenericSchemaA()
        columns = ["test_column_1", "test_column_2"]
        config = json.dumps({"validations": {}, "fields": columns})
        dummy_schema_type = ""
        prepare_schema(dummy_schema_type, config)
        self.assertListEqual(columns, prepare_schema.fields())

    def should_verify_get_config_from_json(self):
        input = '{}'
        expected = {}
        self.assertEqual(expected, GenericSchemaA.get_config_from_json(input))

        input = '{"fields": ["test_column_1", "test_column_2"], "validations": {}}'
        expected = json.loads(input)
        self.assertEqual(expected, GenericSchemaA.get_config_from_json(input))

        input = self.fixtures('test_schema.json')
        expected = {u'fields': [u'test_column_1', u'test_column_2'], u'validations': {u'check_alphanumeric': {u'fields': [u'test_column_1'], u'message': u'Value for {} is {} and it is not alphanumeric.', u'tags': [u'Attribute', u'Data', u'Alpha Numeric']}, u'check_string': {u'fields': [u'test_column_1'], u'message': u'{} does not contain string value', u'constraint': [], u'tags': [u'Attribute', u'Data', u'String']}, u'match_date_format': {u'configs': [{u'fields': [u'test_column_1']}, {u'fields': [u'test_column_2'], u'constraint': [u'YYYY-MM-DD']}], u'message': u'Value for {} is {} and it does not follow date format {}.', u'allow_multiple_config': u'true', u'tags': [u'Attribute', u'Data', u'Date Format']}, u'file_type': {u'fields': [u'FILE'], u'message': u'File {} is not an accepted file type. Accepted file types are {}', u'constraint': [u'csv'], u'tags': [u'File Structure', u'Extension']}, u'file_name': {u'fields': [u'FILE'], u'pre-validation': [], u'constraint': [u'^tbl_account_golden_gate_{}.csv$'], u'message': u"File {} doesn't follow naming format.", u'tags': [u'File Structure', u'Naming']}, u'required': {u'fields': [u'test_column_1', u'test_column_2'], u'message': u'{} has to have value', u'tags': [u'Attribute', u'Data', u'Required']}, u'check_unique': {u'fields': [u'test_column_1'], u'message': u'Value for {} is {} and it is not unique.', u'tags': [u'Attribute', u'Data', u'Unique']}, u'attribute_length': {u'configs': [{u'fields': [u'test_column_1'], u'constraint': [0, 12]}, {u'fields': [u'test_column_2'], u'constraint': [0, 10]}], u'message': u'{} can contain value upto {} char long. {} is above the limit', u'allow_multiple_config': u'true', u'tags': [u'Attribute', u'Data', u'Length']}, u'check_not_null': {u'fields': [u'test_column_1', u'test_column_2'], u'message': u'Value for {} is {} and it should not be null.', u'tags': [u'Attribute', u'Data', u'Not NULL']}, u'match_enum': {u'configs': [{u'fields': [u'test_column_1'], u'pre-validation': [u'str', u'upper_case'], u'constraint': [u'TEST1', u'TEST2']}, {u'fields': [u'test_column_2'], u'pre-validation': [u'str', u'lower_case'], u'constraint': [u'm', u'f', [u'case_sensitive']]}], u'message': u'Value for {} is {} and it is not part of enum list {}.', u'allow_multiple_config': u'true', u'tags': [u'Attribute', u'Data', u'Enumeration']}, u'check_date': {u'fields': [u'test_column_2'], u'message': u'{} does not contain date value', u'tags': [u'Attribute', u'Data', u'Date']}, u'check_column_headers': {u'fields': [u'ALL'], u'message': u'File {} is not an accepted file type. Accepted file types are {}', u'constraint': [u'csv'], u'tags': [u'File Structure', u'Column']}, u'match_regex': {u'configs': [{u'fields': [u'test_column_1'], u'constraint': [u'^[a-z]$']}, {u'fields': [u'test_column_2'], u'constraint': [u'^[a-zA-Z]$']}], u'message': u'Value for {} is {} and it does not match regex {}.', u'allow_multiple_config': u'true', u'tags': [u'Attribute', u'Data', u'Regular Expression']}, u'not_required': {u'fields': [], u'message': u'{} does not contain date value', u'tags': [u'Attribute', u'Data', u'Not Required']}}}
        self.assertEqual(expected, GenericSchemaA.get_config_from_json(input))

        input = 'fixtures/test_schema.json'
        expected = {u'fields': [u'test_column_1', u'test_column_2'], u'validations': {u'check_alphanumeric': {u'fields': [u'test_column_1'], u'message': u'Value for {} is {} and it is not alphanumeric.', u'tags': [u'Attribute', u'Data', u'Alpha Numeric']}, u'check_string': {u'fields': [u'test_column_1'], u'message': u'{} does not contain string value', u'constraint': [], u'tags': [u'Attribute', u'Data', u'String']}, u'match_date_format': {u'configs': [{u'fields': [u'test_column_1']}, {u'fields': [u'test_column_2'], u'constraint': [u'YYYY-MM-DD']}], u'message': u'Value for {} is {} and it does not follow date format {}.', u'allow_multiple_config': u'true', u'tags': [u'Attribute', u'Data', u'Date Format']}, u'file_type': {u'fields': [u'FILE'], u'message': u'File {} is not an accepted file type. Accepted file types are {}', u'constraint': [u'csv'], u'tags': [u'File Structure', u'Extension']}, u'file_name': {u'fields': [u'FILE'], u'pre-validation': [], u'constraint': [u'^tbl_account_golden_gate_{}.csv$'], u'message': u"File {} doesn't follow naming format.", u'tags': [u'File Structure', u'Naming']}, u'required': {u'fields': [u'test_column_1', u'test_column_2'], u'message': u'{} has to have value', u'tags': [u'Attribute', u'Data', u'Required']}, u'check_unique': {u'fields': [u'test_column_1'], u'message': u'Value for {} is {} and it is not unique.', u'tags': [u'Attribute', u'Data', u'Unique']}, u'attribute_length': {u'configs': [{u'fields': [u'test_column_1'], u'constraint': [0, 12]}, {u'fields': [u'test_column_2'], u'constraint': [0, 10]}], u'message': u'{} can contain value upto {} char long. {} is above the limit', u'allow_multiple_config': u'true', u'tags': [u'Attribute', u'Data', u'Length']}, u'check_not_null': {u'fields': [u'test_column_1', u'test_column_2'], u'message': u'Value for {} is {} and it should not be null.', u'tags': [u'Attribute', u'Data', u'Not NULL']}, u'match_enum': {u'configs': [{u'fields': [u'test_column_1'], u'pre-validation': [u'str', u'upper_case'], u'constraint': [u'TEST1', u'TEST2']}, {u'fields': [u'test_column_2'], u'pre-validation': [u'str', u'lower_case'], u'constraint': [u'm', u'f', [u'case_sensitive']]}], u'message': u'Value for {} is {} and it is not part of enum list {}.', u'allow_multiple_config': u'true', u'tags': [u'Attribute', u'Data', u'Enumeration']}, u'check_date': {u'fields': [u'test_column_2'], u'message': u'{} does not contain date value', u'tags': [u'Attribute', u'Data', u'Date']}, u'check_column_headers': {u'fields': [u'ALL'], u'message': u'File {} is not an accepted file type. Accepted file types are {}', u'constraint': [u'csv'], u'tags': [u'File Structure', u'Column']}, u'match_regex': {u'configs': [{u'fields': [u'test_column_1'], u'constraint': [u'^[a-z]$']}, {u'fields': [u'test_column_2'], u'constraint': [u'^[a-zA-Z]$']}], u'message': u'Value for {} is {} and it does not match regex {}.', u'allow_multiple_config': u'true', u'tags': [u'Attribute', u'Data', u'Regular Expression']}, u'not_required': {u'fields': [], u'message': u'{} does not contain date value', u'tags': [u'Attribute', u'Data', u'Not Required']}}}
        self.assertEqual(expected, GenericSchemaA.get_config_from_json(input))

        input = '{"fields": ["test_column_1", "test_column_2"], "validations": {},,,,,,}'
        expected = {'invalid': True}
        self.assertEqual(expected, GenericSchemaA.get_config_from_json(input))

    def should_verify_parsed_schema(self):
        schema_inst = GenericSchemaA()
        columns = ["test_column_1", "test_column_2"]
        input = self.fixtures('test_schema.json')
        dummy_schema_type = ""
        schema_inst(dummy_schema_type, input)
        self.assertEqual([], schema_inst.validations())
        self.assertEqual(columns, schema_inst.fields())


class FeatureSchemaTest(BaseTest):
    def should_verify_custom_validation_mapping(self):
        schema_inst = FeatureSchemaA()
        input = self.fixtures('test_schema.json')
        dummy_schema_type = ""
        schema_inst(dummy_schema_type, input, map={})
        self.assertEqual([], schema_inst.validations())
        self.assertEqual([], schema_inst.fields())
