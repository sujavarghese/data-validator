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


class ReaderPrefixes(Prefixes):
    FILE_EXISTS_PREFIX = "Verify File Exists: "
    FILE_EXTENSION_CHECK_PREFIX = "Verify File Extension: "
    FILE_READER_PREFIX = "Verify File Read: "


class ReaderMessages(Messages):
    FILE_EXISTS_VALIDATION_PASSED = ReaderPrefixes.FILE_EXISTS_PREFIX + Messages.PASSED + ' for {}'
    FILE_EXISTS_VALIDATION_FAILED = ReaderPrefixes.FILE_EXISTS_PREFIX + Messages.FAILED + ' for {}'

    FILE_EXTN_VALIDATION_PASSED = ReaderPrefixes.FILE_EXTENSION_CHECK_PREFIX + Messages.PASSED + 'for extension {} for file {}'
    FILE_EXTN_VALIDATION_FAILED = ReaderPrefixes.FILE_EXTENSION_CHECK_PREFIX + Messages.FAILED + 'for extension {} for file {}'

    FILE_READER_VALIDATION_PASSED = ReaderPrefixes.FILE_READER_PREFIX + Messages.PASSED + ' for {}'
    FILE_READER_VALIDATION_FAILED = ReaderPrefixes.FILE_READER_PREFIX + Messages.FAILED + ' for {} with error: {}'
