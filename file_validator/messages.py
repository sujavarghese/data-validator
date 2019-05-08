from collections import defaultdict
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


class MessageMapping:
    message_code_mapping = defaultdict()

    def __init__(self):
        self.map()

    def map(self):
        self.message_code_mapping.update({
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
        })

    def get_map(self):
        return self.message_code_mapping

    def get_id(self, class_inst):
        cls = type(class_inst)
        return self.get_map().get(cls, None)

