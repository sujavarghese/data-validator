import traceback
from pandas import read_csv, read_excel, read_json
import os.path
from file_validator.reader.messages import ReaderMessages as Messages, ReaderPrefixes as Prefixes
from file_validator.logger import Logger
from file_validator.helper.reader_utils import read_json as read_json_as_dict

logger = Logger()

CSV = "csv"
PSV = "psv"
JSON = "json"
XML = "xml"
XLS = "xls"
XLSX = "xlsx"


class FileExistsMixin:
    log_prefix = Prefixes.FILE_EXISTS_PREFIX

    @staticmethod
    def file_exists(file_path):
        return os.path.isfile(file_path)

    def check_file_exists(self, *args, **kwargs):
        file_path = args[0]

        verified = self.file_exists(file_path)

        msg = Messages.FILE_EXISTS_VALIDATION_PASSED.format(file_path)

        if not verified:
            msg = Messages.FILE_EXISTS_VALIDATION_FAILED.format(file_path)

        logger.record(name=file_path, msg=msg, status=verified)
        return verified


class FileExtensionValidatorMixin:
    log_prefix = Prefixes.FILE_EXTENSION_CHECK_PREFIX
    extensions = {
        CSV: CSV,
        PSV: PSV,
    }

    def extn_valid(self, file_path, file_type):
        extn = self.extensions.get(file_type)
        return extn in file_path

    def check_extn_valid(self, *args, **kwargs):
        file_path = args[0]
        file_type = args[1]

        verified = self.extn_valid(file_path, file_type)

        msg = Messages.FILE_EXTN_VALIDATION_PASSED.format(file_type, file_path)

        if not verified:
            msg = Messages.FILE_EXTN_VALIDATION_FAILED.format(file_type, file_path)

        logger.record(name=file_path, msg=msg, status=verified)
        return verified


class FileReaderMixin:
    """
    Uses Pandas reader methods to read files.
    """
    log_prefix = Prefixes.FILE_READER_PREFIX
    func_map = None

    def set_func_mapping(self):
        self.func_map = {
            CSV: [read_csv, {'dtype': object, 'sep': ','}],
            PSV: [read_csv, {'dtype': object, 'sep': '|'}],
            JSON: [read_json, {}],
            XLS: [read_excel, {}],
            XLSX: [read_excel, {}],
        }

    def read(self, *args, **kwargs):
        as_dict = kwargs.pop('as_dict', None)
        has_read = True
        result = None
        file_path = args[0]
        file_type = args[1]
        msg = Messages.FILE_READER_VALIDATION_PASSED.format(file_path)

        self.set_func_mapping()

        try:
            df = self._read_file(file_path, file_type, **kwargs)
            result = df.to_dict() if as_dict else df
        except Exception as e:
            traceback.print_exc()

            result_dict = read_json_as_dict(file_path)
            result = result_dict if as_dict else None

            if not result or result.get('invalid'):
                has_read = False
                msg = Messages.FILE_READER_VALIDATION_FAILED.format(file_path, e)
        finally:
            logger.record(name=file_path, msg=msg, status=has_read)

            return has_read, logger, result

    def _read_file(self, file_path, file_type, **kwargs):
        options = self.func_map.get(file_type)
        kwargs.update(options[1])

        func = options[0]
        return func(file_path, **kwargs)


class FileReader(FileExistsMixin, FileExtensionValidatorMixin, FileReaderMixin):
    def __init__(self):
        pass

    def validate_and_read(self, *args, **kwargs):
        file_exists = self.check_file_exists(*args, **kwargs)

        if not file_exists:
            return file_exists, logger, None

        return self.read(*args, **kwargs)


class CSVFileReader(FileReader):
    def validate_and_read(self, file_path, file_extn, **kwargs):
        kwargs.pop('check_extn', False)
        valid_extn = self.check_extn_valid(file_path, CSV)

        if not valid_extn:
            return valid_extn, logger, None

        return super(CSVFileReader, self).validate_and_read(file_path, file_extn, **kwargs)


class PSVFileReader(FileReader):
    def validate_and_read(self, file_path, file_extn, **kwargs):
        kwargs.pop('check_extn', False)
        valid_extn = self.check_extn_valid(file_path, PSV)

        if not valid_extn:
            return valid_extn, logger, None

        return super(PSVFileReader, self).validate_and_read(file_path, file_extn, **kwargs)


class JSONFileReader(FileReader):
    def validate_and_read(self, file_path, file_extn, **kwargs):
        should_check_extn = kwargs.pop('check_extn', False)
        if should_check_extn:
            valid_extn = self.check_extn_valid(file_path, JSON)

            if not valid_extn:
                return valid_extn, logger, None

        return super(JSONFileReader, self).validate_and_read(file_path, file_extn, **kwargs)
