import logging
import traceback
from pandas import read_csv
import os.path
from file_validator.reader.messages import ReaderMessages as Messages, ReaderPrefixes as Prefixes
from file_validator.validation_logger import Log, ValidatorLogMixin

logger = logging.getLogger(__name__)

CSV = "csv"
PSV = "psv"
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
            logger.info(msg)

        self._log.make_record(name=file_path, msg=msg, status=verified)
        return verified, msg


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

        msg = Messages.FILE_EXISTS_VALIDATION_PASSED.format(file_type, file_path)

        if not verified:
            msg = Messages.FILE_EXISTS_VALIDATION_FAILED.format(file_type, file_path)
            logger.info(msg)

        self._log.make_record(name=file_path, msg=msg, status=verified)
        return verified, msg


class FileReaderMixin:
    """
    Uses Pandas reader methods to read files.
    """
    log_prefix = Prefixes.FILE_READER_PREFIX
    func_map = {
        CSV: [read_csv, {'dtype': object, 'sep': ','}],
        PSV: [read_csv, {'dtype': object, 'sep': '|'}],
    }

    def read(self, *args, **kwargs):
        has_read = True
        df = None
        file_path = args[0]
        file_type = args[1]
        msg = Messages.FILE_READER_VALIDATION_PASSED.format(file_path)

        try:
            df = self._read_file(file_path, file_type, **kwargs)
        except Exception:
            traceback.print_exc()
            has_read = False
            msg = Messages.FILE_READER_VALIDATION_FAILED.format(file_path)
        finally:
            logger.info(msg)
            self._log.make_record(name=file_path, msg=msg, status=has_read)
            return has_read, df

    def _read_file(self, file_path, file_type, **kwargs):
        options = self.func_map.get(file_type)
        kwargs.update(options[1])

        func = options[0]
        return func(file_path, **kwargs)


class FileReader(FileExistsMixin, FileExtensionValidatorMixin, FileReaderMixin, ValidatorLogMixin):
    def __init__(self, logs=None):
        self._log = Log(logs)

    def validate_and_read(self, *args, **kwargs):
        file_exists = self.check_file_exists(*args, **kwargs)

        if not file_exists:
            return file_exists, self._log

        valid_extn = self.check_extn_valid(*args, **kwargs)

        if not valid_extn:
            return valid_extn, self._log

        return self.read(*args, **kwargs)
