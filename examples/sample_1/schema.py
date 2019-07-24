from file_validator.schema.schema import FeatureSchema
from examples.sample_1.validator import CustomRule


class ContactsSchema(FeatureSchema):
    map = {
        'check_xyz': CustomRule
    }
