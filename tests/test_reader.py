from tests import TestCase
from file_validator.reader.messages import ReaderPrefixes, ReaderMessages
from file_validator.reader.reader import (
    FileExistsMixin, logger, FileExtensionValidatorMixin, FileReaderMixin
)


class TestReaderPrefixes(TestCase):
    def setUp(self) -> None:
        self.instance = ReaderPrefixes()

    def test_should_verify_get(self):
        self.assertEqual("Verify File Exists: ", self.instance.get('FILE_EXISTS_PREFIX'))
        self.assertEqual("Verify File Extension: ", self.instance.get('FILE_EXTENSION_CHECK_PREFIX'))
        self.assertEqual("Verify File Read: ", self.instance.get('FILE_READER_PREFIX'))

    def test_should_verify_all(self):
        self.assertEqual(3, len(self.instance.all()))


class TestReaderMessages(TestCase):
    def setUp(self) -> None:
        self.instance = ReaderMessages()

    def test_should_verify_message_starts_with_prefix(self):
        messages = self.instance.all()
        prefices = ReaderPrefixes().all()

        for message in messages:
            self.assertEqual(True, any([True for prefix in prefices if message.startswith(prefix)]))


class FileExistsMixinTest(FileExistsMixin):
    pass


class TestFileExistsMixin(TestCase):
    def setUp(self) -> None:
        self.instance = FileExistsMixinTest()
        self.logger = logger

    def test_should_check_file_exists(self):
        path = self.path("tbl_account.csv")
        self.assertEqual(True, self.instance.check_file_exists(path))
        serialized_logs = [(
            self.basepath + '/fixtures/tbl_account.csv',
            '<LogRecord: name=' + self.basepath + '/fixtures/tbl_account.csv, status=True, message=Verify File Exists: Passed for ' + self.basepath + '/fixtures/tbl_account.csv>'
        )]
        self.assertEqual(serialized_logs, self.logger.serialize(clear=True))

    def test_should_fail_file_exists_check(self):
        path = self.path("tbl_contact.csv")
        self.assertEqual(False, self.instance.check_file_exists(path))
        serialized_logs = [(
            self.basepath + '/fixtures/tbl_contact.csv',
            '<LogRecord: name=' + self.basepath + '/fixtures/tbl_contact.csv, status=False, message=Verify File Exists: Failed for ' + self.basepath + '/fixtures/tbl_contact.csv>'
        )]
        self.assertEqual(serialized_logs, self.logger.serialize(clear=True))


class FileExtensionValidatorMixinTest(FileExtensionValidatorMixin):
    pass


class TestFileExtensionValidatorMixin(TestCase):
    def setUp(self) -> None:
        self.instance = FileExtensionValidatorMixinTest()
        self.logger = logger

    def test_should_verify_valid_extn(self):
        path = self.path("tbl_account.csv")  # file exists
        self.assertEqual(True, self.instance.check_extn_valid(path, 'csv'))  # valid extension
        self.assertEqual(
            '<LogRecord: name=' + self.basepath + '/fixtures/tbl_account.csv, status=True, message=Verify File Extension: Passed for extension csv for file ' + self.basepath + '/fixtures/tbl_account.csv>',
            self.logger.serialize(clear=True)[0][1])
        path = self.path("tbl_contact.csv")  # file does not exists
        self.assertEqual(True, self.instance.check_extn_valid(path, 'csv'))  # valid extension
        self.assertTrue("True" in self.logger.serialize(clear=True)[0][1])

    def test_should_fail_extn_valid_check(self):
        path = self.path("tbl_account.csv")
        self.assertEqual(False, self.instance.check_extn_valid(path, 'psv'))  # invalid extension
        self.assertTrue("False" in self.logger.serialize(clear=True)[0][1])
        path = self.path("test_schema.json")
        # "json" is not part of allowed extensions list.
        self.assertEqual(False, self.instance.check_extn_valid(path, 'json'))
        self.assertTrue("False" in self.logger.serialize(clear=True)[0][1])


class FileReaderMixinTest(FileReaderMixin):
    pass


class TestFileReaderMixin(TestCase):
    """
    For file read, refer - test_should_verify_file_read, test_should_verify_json_file_read.
    """
    def setUp(self) -> None:
        self.instance = FileReaderMixinTest()

    def test_should_verify_func_mapping(self):
        # allowed types are csv, psv, json, excel
        self.instance.set_func_mapping()
        self.assertIsNotNone(self.instance.func_map.get('csv'))
        self.assertIsNotNone(self.instance.func_map.get('psv'))
        self.assertIsNotNone(self.instance.func_map.get('json'))
        self.assertIsNone(self.instance.func_map.get('xml'))
        self.assertIsNotNone(self.instance.func_map.get('xls'))
        self.assertIsNotNone(self.instance.func_map.get('xlsx'))
        self.assertIsNone(self.instance.func_map.get('txt'))

    def test_should_verify_file_read(self):
        path = self.path("tbl_account.csv")  # file exists
        status, log, result = self.instance.read(path, 'csv', as_dict=True)
        self.assertTrue(status)
        self.assertTrue('True' in log.serialize(clear=True)[0][1])
        self.assertEqual({
            'test_column_1': {0: 'test1', 1: '1', 2: '1', 3: '12/01/1989'},
            'test_column_2': {0: 'test2/test1/test3', 1: '2', 2: '3.09', 3: '30/01/1989'}
        }, result)

    def test_should_verify_json_file_read(self):
        path = self.path("test_schema.json")  # config file
        status, log, result = self.instance.read(path, 'json', as_dict=True, is_config=True)
        self.assertTrue(status)
        self.assertTrue('True' in log.serialize(clear=True)[0][1])
        self.assertEqual({
            'fields': ['test_column_1'],
            'unique': ['test_column_1'],
            'validations': {
                'file_name': {'constraint': ['tbl_account.csv'],
                              'fields': ['FILE'],
                              'message': "{} doesn't follow naming format.",
                              'pre-validation': [],
                              'tags': ['File Structure', 'Naming']}}
        }, result)
