import traceback
from pandas import read_csv, read_excel, read_json
import os.path
from file_validator.reader.messages import ReaderMessages as Messages, ReaderPrefixes as Prefixes
from file_validator.logger import Logger
from file_validator.helper.utils import read_json as read_json_as_dict

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

    def check_file_exists(self, file_path, **kwargs):
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
        if not extn:
            return False

        return extn in file_path

    def check_extn_valid(self, file_path, file_type=None):
        if not file_type:
            file_type = self.get_extn()

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

    def read(self, file_path, file_type=None, as_dict=False, is_config=False, *args, **kwargs):
        has_read = True
        result = None
        msg = Messages.FILE_READER_VALIDATION_PASSED.format(file_path)

        self.set_func_mapping()

        try:
            if is_config and file_type == JSON:
                raise Exception("Don't use pandas to read json config")

            df = self._read_file(file_path, file_type, **kwargs)
            result = df.to_dict() if as_dict else df
        except Exception as e:
            traceback.print_exc()

            if file_type == JSON:
                result_dict = read_json_as_dict(file_path)
                result = result_dict if as_dict else None

            if not result or result.get('invalid'):
                has_read = False
                msg = Messages.FILE_READER_VALIDATION_FAILED.format(file_path, e)
                result = {'invalid': True, 'message': e.args}
        finally:
            logger.record(name=file_path, msg=msg, status=has_read)

            return has_read, logger, result

    def _read_file(self, file_path, file_type, **kwargs):
        options = self.func_map.get(file_type or self.get_extn(), {})
        kwargs.update(options[1])

        func = options[0]
        return func(file_path, **kwargs)


class FileReader(FileExistsMixin, FileExtensionValidatorMixin, FileReaderMixin):
    extn = None

    def __init__(self):
        pass

    def get_extn(self):
        return self.extn

    def validate_and_read(self, file_path, file_extn=None, *args, **kwargs):
        should_check_extn = kwargs.pop('check_extn', False)

        if should_check_extn:
            valid_extn = self.check_extn_valid(file_path, file_extn)

            if not valid_extn:
                return valid_extn, logger, None

        file_exists = self.check_file_exists(file_path, **kwargs)

        if not file_exists:
            return file_exists, logger, None

        return self.read(file_path, file_extn, *args, **kwargs)


class CSVFileReader(FileReader):
    extn = CSV


class PSVFileReader(FileReader):
    extn = PSV


class JSONFileReader(FileReader):
    extn = JSON
