from file_validator.validator.rules import *


class Base(object):
    def all(self):
        return [name for name, value in vars(self).items() if not name.startswith('_')]

    def get(self, key):
        getattr(self, key, None)


class MessageCodes(Base):
    CDP_FL_001 = "CDP_FL_001"
    CDP_FL_002 = "CDP_FL_002"
    CDP_FL_003 = "CDP_FL_003"
    CDP_FL_004 = "CDP_FL_004"
    CDP_FL_005 = "CDP_FL_005"
    CDP_FL_006 = "CDP_FL_006"

    CDP_AT_001 = "CDP_AT_001"
    CDP_AT_002 = "CDP_AT_002"
    CDP_AT_003 = "CDP_AT_003"
    CDP_AT_004 = "CDP_AT_004"
    CDP_AT_005 = "CDP_AT_005"
    CDP_AT_006 = "CDP_AT_006"
    CDP_AT_007 = "CDP_AT_007"
    CDP_AT_008 = "CDP_AT_008"
    CDP_AT_009 = "CDP_AT_009"
    CDP_AT_010 = "CDP_AT_010"
    CDP_AT_011 = "CDP_AT_011"
    CDP_AT_012 = "CDP_AT_012"
    CDP_AT_013 = "CDP_AT_013"

    def codes(self):
        return [value for name, value in vars(self).items() if not name.startswith('_')]

    def duplicate(self, code):
        return False if code in self.all() or code in self.codes() else True


class MessageMapping:
    message_code_mapping = {
        # File validation mapping
        FileNameValidation: MessageCodes.CDP_FL_001,
        FileTypeValidation: MessageCodes.CDP_FL_002,
        HeaderValidation: MessageCodes.CDP_FL_003,
        # Attribute validation mapping
        DataTypeAttributeValidation: MessageCodes.CDP_AT_001,
        IsStringAttributeValidation: MessageCodes.CDP_AT_002,
        IsNullAttributeValidation: MessageCodes.CDP_AT_003,
        RequiredAttributeValidation: MessageCodes.CDP_AT_004,
        IsDateAttributeValidation: MessageCodes.CDP_AT_005,
        AttributeLengthValidation: MessageCodes.CDP_AT_006,
        RegexAttributeValidation: MessageCodes.CDP_AT_007,
        EnumAttributeValidation: MessageCodes.CDP_AT_008,
        DateFormatAttributeValidation: MessageCodes.CDP_AT_009,
        AlphaNumericAttributeValidation: MessageCodes.CDP_AT_010,
        EmailValidation: MessageCodes.CDP_AT_011,
        PhoneValidation: MessageCodes.CDP_AT_012,
        IsIntegerAttributeValidation: MessageCodes.CDP_AT_013,
    }

    def __init__(self, mapping_dict={}):
        duplicates = self.has_duplicates(mapping_dict)
        if duplicates:
            print("""Some of Rules/Codes mappings duplicated. Please verify provided mapping. Duplicated Rules: '{}', 
            Duplicated Message codes: '{}'. Continuing execution...""".format(duplicates[0], duplicates[1]))
        self.map(mapping_dict)

    def map(self, mapping):
        self.message_code_mapping.update(mapping)

    def get_map(self):
        return self.message_code_mapping

    def get_id(self, class_inst):
        cls = type(class_inst)
        return self.get_map().get(cls, None)

    def has_duplicates(self, mapping_dict):
        rules = mapping_dict.keys()
        codes = mapping_dict.values()
        duplicate_rules = set(rules).intersection(set(self.message_code_mapping.keys()))
        duplicate_codes = set(codes).intersection(set(self.message_code_mapping.values()))
        [duplicate_rules.add(rule) for rule in rules if list(rules).count(rule) > 1]
        [duplicate_codes.add(code) for code in codes if list(codes).count(code) > 1]

        if duplicate_rules or duplicate_codes:
            return [duplicate_rules, duplicate_codes]
        return False
