from file_validator.messages import Prefixes, Messages


class ValidatorPrefixes(Prefixes):
    FILE_NAME_PREFIX = "Verify File Name: "
    FILE_EXTN_PREFIX = "Verify File Extension: "
    HEADER_VALIDATOR_PREFIX = "Verify field names: "
    COLUMN_VALIDATOR_PREFIX = "Verify field values: "


class ValidatorMessages(Messages):
    FILE_NAME_VALIDATION_PASSED = ValidatorPrefixes.FILE_NAME_PREFIX + Messages.PASSED + ' for {}'
    FILE_NAME_VALIDATION_FAILED = ValidatorPrefixes.FILE_NAME_PREFIX + Messages.FAILED + ' for {}. Expected format is {}'

    FILE_EXTN_VALIDATION_PASSED = ValidatorPrefixes.FILE_NAME_PREFIX + Messages.PASSED + ' for {}'
    FILE_EXTN_VALIDATION_FAILED = ValidatorPrefixes.FILE_NAME_PREFIX + Messages.FAILED + ' for {}. Expected format is {}'

    HEADER_VALIDATION_PASSED = ValidatorPrefixes.HEADER_VALIDATOR_PREFIX + Messages.PASSED + ' for {}'
    HEADER_VALIDATION_FAILED = ValidatorPrefixes.HEADER_VALIDATOR_PREFIX + Messages.FAILED + ' for {}'
    HEADER_VALIDATION_FAILED_WITH_NO_FILE = ValidatorPrefixes.HEADER_VALIDATOR_PREFIX + Messages.FAILED + \
        ' No file validation schema specified. Passing through...'
    HEADER_VALIDATION_FAILED_WITH_MISSING_COLUMN = ValidatorPrefixes.HEADER_VALIDATOR_PREFIX + Messages.FAILED + \
        ' Missing columns are {}'
