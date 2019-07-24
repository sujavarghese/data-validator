from file_validator.validator.rules import AttributeValidation
from file_validator.validator.validator import Validator
from examples import ValidatorMessages


class CustomRule(AttributeValidation):
    message = ValidatorMessages.FILE_EXTN_VALIDATION_FAILED

    def _execute(self, record, **kwargs):
        super(CustomRule, self)._execute(record, **kwargs)
        return True


class CustomValidator(Validator):
    pass

