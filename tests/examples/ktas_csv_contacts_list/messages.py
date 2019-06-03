from file_validator.validator import Messages
from file_validator.messages import MessageCodes as Code


class ValidatorMessages(Messages):
    FILE_EXTN_VALIDATION_FAILED = "Failed"


class ReaderMessages(Messages):
    FILE_EXTN_VALIDATION_FAILED = "Failed"


class MessageCodes(Code):
    CDP_AT_051 = "CDP_AT_051"

