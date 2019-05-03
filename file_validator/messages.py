from collections import defaultdict


class Base(object):
    def all(self):
        return [name for name, value in vars(self).items() if not name.startswith('_')]

    def get(self, key):
        getattr(self, key, None)


class Prefixes(Base):
    pass


class Messages(Base):
    FAILED = "Failed"
    PASSED = "Passed"


class MessageCodes(Base):
    CDP_001 = "CDP_001"
    CDP_002 = "CDP_002"
    CDP_003 = "CDP_003"
    CDP_004 = "CDP_004"
    CDP_005 = "CDP_005"
    CDP_006 = "CDP_006"
    CDP_007 = "CDP_007"
    CDP_008 = "CDP_008"
    CDP_009 = "CDP_009"
    CDP_010 = "CDP_010"


class MessageMapping:
    message_code_mapping = defaultdict()

    def map(self):
        from file_validator.reader.messages import ReaderMessages
        from file_validator.validator.messages import ValidatorMessages
        self.message_code_mapping.update({
            MessageCodes.CDP_001: ReaderMessages.FILE_EXISTS_VALIDATION_PASSED,
            MessageCodes.CDP_002: ReaderMessages.FILE_EXISTS_VALIDATION_FAILED,
            MessageCodes.CDP_003: ReaderMessages.FILE_EXTN_VALIDATION_PASSED,
            MessageCodes.CDP_004: ReaderMessages.FILE_EXTN_VALIDATION_FAILED,
            MessageCodes.CDP_005: ReaderMessages.FILE_READER_VALIDATION_PASSED,
            MessageCodes.CDP_006: ReaderMessages.FILE_READER_VALIDATION_FAILED,
            MessageCodes.CDP_007: ValidatorMessages.HEADER_VALIDATION_PASSED,
            MessageCodes.CDP_008: ValidatorMessages.HEADER_VALIDATION_FAILED,
            MessageCodes.CDP_009: ValidatorMessages.HEADER_VALIDATION_FAILED_WITH_NO_FILE,
            MessageCodes.CDP_010: ValidatorMessages.HEADER_VALIDATION_FAILED_WITH_MISSING_COLUMN,

        })

    def get_map(self):
        return self.message_code_mapping

