import logging
import traceback
import pandas as pd
from pandas.io.parsers import TextFileReader
from file_validator.helper import reader_utils
from file_validator.validator.messages import ValidatorMessages as Messages, ValidatorPrefixes as Prefixes
from file_validator.validation_logger import Log, ValidatorLogMixin

logger = logging.getLogger(__name__)


class HeaderValidatorMixin:
    log_prefix = Prefixes.HEADER_VALIDATOR_PREFIX

    def verify_headers(self, df, file_path, file_type, **kwargs):
        verified = True
        msg = Messages.HEADER_VALIDATION_PASSED.format(file_path)

        try:
            if isinstance(df, TextFileReader):
                logger.info('Reading in chunks...')
                for idx, tfr in enumerate(df):
                    logger.info('chunk: {}'.format(idx))
                    verified, msg = self._verify_headers(tfr, file_path, file_type, **kwargs)
                    if not verified:
                        break
            else:
                logger.info('Reading everything...')
                verified, msg = self._verify_headers(df, file_path, file_type, **kwargs)

        except Exception as e:
            traceback.print_exc()
            verified = False
            msg = Messages.HEADER_VALIDATION_FAILED.format(file_path)

        logger.info(msg)
        self._log.make_record(name=file_path, msg=msg, status=verified)

        return verified, msg

    def _verify_headers(self, df, file_path, file_type, **kwargs):
        logger.info('{}: {}'.format(self.log_prefix, file_path))

        verified = True
        msg = Messages.HEADER_VALIDATION_PASSED.format(file_path)

        data_schema = kwargs.get('schema')
        if not data_schema:
            verified = False
            msg = Messages.HEADER_VALIDATION_FAILED_WITH_NO_FILE
            return verified, msg

        # TODO: implement schema factory and add method to fetch columns. accept option 'required=true'
        required_columns = data_schema(file_type).columns(required=True)

        if not required_columns:
            return verified, msg

        columns = list(df.columns.values)

        if sorted(columns) == sorted(required_columns):
            return verified, msg

        missing_columns = set(required_columns).difference(set(columns))
        if len(missing_columns) == 0:
            return verified, msg

        verified = False
        msg = Messages.HEADER_VALIDATION_FAILED_WITH_MISSING_COLUMN.format(missing_columns)

        return verified, msg


class DataFrameValidationMixin:
    log_prefix = Prefixes.COLUMN_VALIDATOR_PREFIX

    def execute(self, func, row):
        try:
            result = func(row)
        except Exception:
            result = None

        if result:
            return True
        return False

    def verify_dataframe_values(self, df, file_type, **kwargs):
        data_schema = kwargs.get('schema')(file_type)
        should_store_pass = kwargs.get("should_store_pass", False)
        schema_fields = data_schema.columns(required=True)

        ignored_columns = [col for col in df.columns if col not in schema_fields]
        logger.info('Source columns {} will be ignored.'.format(ignored_columns))

        for field, (func, custom) in data_schema.validations():

            logger.info("{} for field {}, with method '{}'".format(self.log_prefix, field, func))

            if not custom:
                result_df = df[field].apply(lambda row: self.execute(func, row), axis=1)
            else:
                result_df = df.apply(lambda row: self.execute(func, row), axis=1)

            combined = pd.concat([df[field], result_df])

            for row in combined.itertuples():
                index = row[0]
                value = row[1]
                is_valid = row[2]
                if is_valid:
                    msg = Messages.COLUMNS_VALIDATION_PASSED
                else:
                    msg = Messages.COLUMNS_VALIDATION_FAILED

                msg = msg.format(field, func, value)

                if (is_valid and should_store_pass) or not is_valid:
                    logger.info(msg)
                    self._log.make_record(name=field, msg=msg, status=is_valid)

        logger.info("{} ended".format(self.log_prefix))


class Validator(HeaderValidatorMixin, DataFrameValidationMixin, ValidatorLogMixin):
    def __init__(self, logs=None):
        self._log = Log(logs)

    def validate_fields(self, df, *args, **kwargs):
        file_path = args[0]
        file_type = args[1]

        df = reader_utils.clean_column_names(df)

        required_headers_present, msg = self.verify_headers(df, file_path, file_type, **kwargs)

        if not required_headers_present:
            return required_headers_present, self._log

        structure_logs = self._log
        self._log = Log()

        self.verify_dataframe_values(df, file_type, **kwargs)

        return True, structure_logs, self._log
