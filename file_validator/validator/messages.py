from file_validator.messages import Prefixes, Messages


class ValidatorPrefixes(Prefixes):
    HEADER_VALIDATOR_PREFIX = "Verify the field names: "
    COLUMN_VALIDATOR_PREFIX = "Verify the field values: "


class ValidatorMessages(Messages):
    HEADER_VALIDATION_PASSED = ValidatorPrefixes.HEADER_VALIDATOR_PREFIX + Messages.PASSED + ' for {}'
    HEADER_VALIDATION_FAILED = ValidatorPrefixes.HEADER_VALIDATOR_PREFIX + Messages.FAILED + ' for {}'
    HEADER_VALIDATION_FAILED_WITH_NO_FILE = ValidatorPrefixes.HEADER_VALIDATOR_PREFIX + Messages.FAILED + \
        ' No File Schema specified. Passing through...'
    HEADER_VALIDATION_FAILED_WITH_MISSING_COLUMN = ValidatorPrefixes.HEADER_VALIDATOR_PREFIX + Messages.FAILED + \
        ' Missing columns are {}'

    COLUMNS_VALIDATION_PASSED = ValidatorPrefixes.COLUMN_VALIDATOR_PREFIX + Messages.PASSED + ' for field {}. Applied rule is {} and failed for value {}'
    COLUMNS_VALIDATION_FAILED = ValidatorPrefixes.COLUMN_VALIDATOR_PREFIX + Messages.FAILED + ' for field {}. Applied rule is {} and failed for value {}'
