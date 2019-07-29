from tests import TestCase
from file_validator.reader.messages import ReaderPrefixes, ReaderMessages
from file_validator.reader.reader import (
    FileExistsMixin, logger, FileExtensionValidatorMixin, FileReaderMixin, FileReader, CSVFileReader, PSVFileReader,
    JSONFileReader
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
    extn = 'csv'

    def get_extn(self):
        return self.extn


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

        path = self.path("tbl_account.csv")
        self.assertEqual(True, self.instance.check_extn_valid(path))  # no extension, default from class
        self.assertTrue("True" in self.logger.serialize(clear=True)[0][1])

    def test_should_fail_extn_valid_check(self):
        path = self.path("tbl_account.csv")
        self.assertEqual(False, self.instance.check_extn_valid(path, 'psv'))  # invalid extension
        self.assertTrue("False" in self.logger.serialize(clear=True)[0][1])

        self.instance.extn = None
        path = self.path("tbl_account.csv")
        self.assertEqual(False, self.instance.check_extn_valid(path))  # no extension, default from class
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

    def test_should_verify_file_read_mixin(self):
        path = self.path("tbl_account.csv")  # file exists
        status, log, result = self.instance.read(path, 'csv', as_dict=True)
        self.assertTrue(status)
        self.assertTrue('True' in log.serialize(clear=True)[0][1])
        self.assertEqual({
            'test_column_1': {0: 'test1', 1: '1', 2: '1', 3: '12/01/1989'},
            'test_column_2': {0: 'test2/test1/test3', 1: '2', 2: '3.09', 3: '30/01/1989'}
        }, result)

    def test_should_verify_json_file_read_mixin(self):
        path = self.path("test_schema.json")  # config file
        status, log, result = self.instance.read(path, 'json', as_dict=True, is_config=True)
        self.assertTrue(status)
        self.assertTrue('True' in log.serialize(clear=True)[0][1])
        self.assertEqual({
            'fields': ['test_column_1'],
            'unique': ['test_column_1'],
            'validations': {
                'file_name': {
                    'constraint': ['tbl_account.csv'],
                    'fields': ['FILE'],
                    'message': "{} doesn't follow naming format.",
                    'pre-validation': [],
                    'tags': ['File Structure', 'Naming']
                }
            }
        }, result)

    def test_should_fail_for_invalid_csv_file_read_mixin(self):
        path = self.path("test.csv")  # non existing csv file
        status, log, result = self.instance.read(path, 'csv')
        self.assertFalse(status)
        logs = [(
            self.basepath + '/fixtures/test.csv',
            "<LogRecord: name=" + self.basepath + "/fixtures/test.csv, status=False, message=Verify File Read: Failed for "+
            self.basepath +"/fixtures/test.csv with error: File b'"+self.basepath+"/fixtures/test.csv' does not exist>"
        )]
        self.assertEqual(logs, log.serialize(clear=True))
        self.assertTrue(result.get('invalid'))
        self.assertEqual(
            ("File b'" + self.basepath + "/fixtures/test.csv' does not exist",),
            result.get('message')
        )

    def test_should_fail_for_invalid_json_file_read_mixin_1(self):
        path = self.path("test.json")  # non existing json file
        status, log, result = self.instance.read(path, 'json')
        self.assertFalse(status)
        logs = [(
            self.basepath + '/fixtures/test.json',
            "<LogRecord: name=" + self.basepath + "/fixtures/test.json, status=False, message=Verify File Read: Failed for " +
            self.basepath + "/fixtures/test.json with error: Expected object or value>"
        )]
        self.assertEqual(logs, log.serialize(clear=True))
        self.assertTrue(result.get('invalid'))
        self.assertEqual(
            ('Expected object or value',),
            result.get('message')
        )

    def test_should_fail_for_invalid_json_file_read_mixin_2(self):
        path = self.path("test.json")  # non existing file with as_dict=True
        status, log, result = self.instance.read(path, 'json', as_dict=True)
        self.assertFalse(status)
        logs = [(
            self.basepath + '/fixtures/test.json',
            "<LogRecord: name=" + self.basepath + "/fixtures/test.json, status=False, message=Verify File Read: Failed for " +
            self.basepath + "/fixtures/test.json with error: Expected object or value>"
        )]
        self.assertEqual(logs, log.serialize(clear=True))
        self.assertTrue(result.get('invalid'))
        self.assertEqual(
            ('Expected object or value',),
            result.get('message')
        )

    def test_should_fail_for_invalid_json_file_read_mixin_3(self):
        path = self.path("test.json")  # non existing file with is_config=True
        status, log, result = self.instance.read(path, 'json', is_config=True)
        self.assertFalse(status)
        logs = [(
            self.basepath + '/fixtures/test.json',
            "<LogRecord: name=" + self.basepath + "/fixtures/test.json, status=False, message=Verify File Read: Failed for " +
            self.basepath + "/fixtures/test.json with error: Don't use pandas to read json config>"
        )]
        self.assertEqual(logs, log.serialize(clear=True))
        self.assertTrue(result.get('invalid'))
        self.assertEqual(
            ("Don't use pandas to read json config",),
            result.get('message')
        )


class FileReaderTest(FileReader):
    extn = 'csv'


class TestFileReader(TestCase):
    """
    For file read, refer - test_should_verify_file_read, test_should_verify_json_file_read.
    """
    def setUp(self) -> None:
        self.instance = FileReaderTest()

    def test_should_verify_csv_file_reader(self):
        path = self.path("tbl_account.csv")  # file exists
        status, log, result = self.instance.validate_and_read(path, as_dict=True)
        self.assertTrue(status)
        logs = [(
            self.basepath + '/fixtures/tbl_account.csv',
            '<LogRecord: name=' + self.basepath + '/fixtures/tbl_account.csv, status=True, message=Verify File Exists: Passed for '
            + self.basepath + '/fixtures/tbl_account.csv>'),
            (self.basepath + '/fixtures/tbl_account.csv', '<LogRecord: name=' + self.basepath +
             '/fixtures/tbl_account.csv, status=True, message=Verify File Read: Passed for ' + self.basepath + '/fixtures/tbl_account.csv>')
        ]
        self.assertEqual(logs, log.serialize(clear=True))
        self.assertEqual({
            'test_column_1': {0: 'test1', 1: '1', 2: '1', 3: '12/01/1989'},
            'test_column_2': {0: 'test2/test1/test3', 1: '2', 2: '3.09', 3: '30/01/1989'}
        }, result)

    def test_should_fail_csv_file_reader(self):
        path = self.path("account.csv")  # file exists
        status, log, result = self.instance.validate_and_read(path, as_dict=True)
        self.assertFalse(status)
        logs = [(
            self.basepath + '/fixtures/account.csv',
            "<LogRecord: name=" + self.basepath + "/fixtures/account.csv, status=False, message=Verify File Exists: Failed for " +
            self.basepath + '/fixtures/account.csv>'
        )]
        self.assertEqual(logs, log.serialize(clear=True))
        self.assertEqual(None, result)

    def test_should_fail_csv_file_with_wrong_extension(self):
        path = self.path("tbl_account.csv")  # file exists
        status, log, result = self.instance.validate_and_read(path, file_extn='xml', as_dict=True, check_extn=True)
        self.assertFalse(status)
        self.assertIsNone(result)

        path = self.path("tbl_account.csv")  # file exists
        status, log, result = self.instance.validate_and_read(path, file_extn='json', as_dict=True, check_extn=True)
        self.assertFalse(status)
        self.assertIsNone(result)

        path = self.path("tbl_account.csv")  # file exists
        status, log, result = self.instance.validate_and_read(path, file_extn='psv', as_dict=True, check_extn=True)
        self.assertFalse(status)
        self.assertIsNone(result)

        logs = [
            (self.basepath +'/fixtures/tbl_account.csv', '<LogRecord: name=' + self.basepath + '/fixtures/tbl_account.csv, '
                'status=False, message=Verify File Extension: Failed for extension xml for file ' + self.basepath +
                '/fixtures/tbl_account.csv>'),
            (self.basepath +'/fixtures/tbl_account.csv', '<LogRecord: name=' + self.basepath + '/fixtures/tbl_account.csv, '
                'status=False, message=Verify File Extension: Failed for extension json for file ' + self.basepath +
             '/fixtures/tbl_account.csv>'),
            (self.basepath +'/fixtures/tbl_account.csv', '<LogRecord: name=' + self.basepath + '/fixtures/tbl_account.csv, '
                'status=False, message=Verify File Extension: Failed for extension psv for file ' + self.basepath +
             '/fixtures/tbl_account.csv>')
         ]
        self.assertEqual(logs, log.serialize(clear=True))

    def test_should_fail_non_existing_file(self):
        path = self.path("tbl_contact.csv")
        status, log, result = self.instance.validate_and_read(path, file_extn='csv')
        self.assertFalse(status)
        self.assertIsNone(result)

        path = self.path("tbl_contact.csv")
        status, log, result = self.instance.validate_and_read(path, file_extn='csv', as_dict=True)
        self.assertFalse(status)
        self.assertIsNone(result)

        path = self.path("tbl_contact.csv")
        status, log, result = self.instance.validate_and_read(path, file_extn='csv', as_dict=True, is_config=True)
        self.assertFalse(status)
        self.assertIsNone(result)

        logs = [
            (self.basepath +'/fixtures/tbl_contact.csv', '<LogRecord: name=' + self.basepath + '/fixtures/tbl_contact.csv, '
                'status=False, message=Verify File Exists: Failed for ' + self.basepath +
                '/fixtures/tbl_contact.csv>'),
            (self.basepath +'/fixtures/tbl_contact.csv', '<LogRecord: name=' + self.basepath + '/fixtures/tbl_contact.csv, '
                'status=False, message=Verify File Exists: Failed for ' + self.basepath +
             '/fixtures/tbl_contact.csv>'),
            (self.basepath +'/fixtures/tbl_contact.csv', '<LogRecord: name=' + self.basepath + '/fixtures/tbl_contact.csv, '
                'status=False, message=Verify File Exists: Failed for ' + self.basepath +
             '/fixtures/tbl_contact.csv>')
         ]
        self.assertEqual(logs, log.serialize(clear=True))


class TestCSVFileReader(TestCase):
    class CSVFileReaderTest(CSVFileReader):pass

    def test_should_verify_extn(self):
        instance = self.CSVFileReaderTest()
        self.assertEqual('csv', instance.get_extn())


class TestPSVFileReader(TestCase):
    class PSVFileReaderTest(PSVFileReader):pass

    def test_should_verify_extn(self):
        instance = self.PSVFileReaderTest()
        self.assertEqual('psv', instance.get_extn())


class JSONFileReaderTest(JSONFileReader):
    pass


class TestJSONFileReader(TestCase):
    class JSONFileReaderTest(JSONFileReader):pass

    def test_should_verify_extn(self):
        instance = self.JSONFileReaderTest()
        self.assertEqual('json', instance.get_extn())
