from file_validator.schema.schema import FeatureSchema
from examples.ktas_csv_contacts_list.validator import CustomRule


class ContactsSchema(FeatureSchema):
    map = {
        'check_xyz': CustomRule
    }
