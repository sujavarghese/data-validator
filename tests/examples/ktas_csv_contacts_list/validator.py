from file_validator.validator.rules import AttributeValidation
from file_validator.validator.validator import Validator
from tests.examples.ktas_csv_contacts_list.messages import ValidatorMessages, MessageCodes
from file_validator.messages import MessageMapping


class CustomRule(AttributeValidation):
    message = ValidatorMessages.FILE_EXTN_VALIDATION_FAILED

    def execute(self, record, **kwargs):
        super(CustomRule, self)._execute(record, **kwargs)
        return True


class CustomValidator(Validator):
    pass


class MessageMap(MessageMapping):
    def __init__(self):
        super(MessageMap, self).__init__({
            CustomRule: MessageCodes.CDP_AT_051,
        })
