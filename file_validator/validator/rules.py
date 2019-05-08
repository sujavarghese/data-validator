import re
import os
from file_validator.validator.utils import (
    empty, is_date, required, clean_value
)
from file_validator.validator.messages import ValidatorMessages


class Base(object):
    validate_key = None
    attribute = None
    unique_key = None
    constraint = None
    is_file_rule = False
    message = ""
    tags = []
    pre_validation = []
    _passed_objects = []
    _failed_objects = []
    _failed_info = []
    _passed = True
    _failed = False

    def __str__(self):
        return self.name()

    __repr__ = __str__

    def __init__(self, validate_key, attribute, unique_key, constraint, message, tags, pre_validation):
        self.validate_key = validate_key
        self.attribute = attribute
        self.unique_key = unique_key
        self.constraint = constraint
        self.message = message
        self.tags = tags
        self.pre_validation = pre_validation
        self._attr_value = None

    def name(self):
        return "{}<key={},attribute={}".format(
            self.__class__.__name__, self.validate_key, self.attribute
        )

    def get_value(self, record):
        return record
        # return record.get(self.attribute, None)

    def execute(self, record, **kwargs):
        raise NotImplementedError()

    def pass_message(self, *args, **kwargs):
        return "{} on column {} passed for record {}".format(self.__class__.__name__, self.attribute, args[0])

    def process_result(self, result_df):
        self._passed_objects = result_df[result_df[self.name()] == True]
        self._failed_objects = result_df[result_df[self.name()] == False]

    def failed_info(self):
        return self._failed_info

    def fail_message(self, *args, **kwargs):
        return self.message.format(args, **kwargs)

    def passed_objects(self):
        return self._passed_objects

    def failed_objects(self):
        return self._failed_objects


class FileValidation(Base):
    tags = ["File Structure"]
    is_file_rule = True

    def fail_message(self, *args, **kwargs):
        return self.message.format(args, self.failed_info())

    def execute(self, record, **kwargs):
        raise NotImplementedError()


class AttributeValidation(Base):
    tags = ["Attribute"]

    def fail_message(self, *args, **kwargs):
        failed_record = args[0]
        return self.message.format(clean_value(failed_record[self.attribute]))

    def execute(self, record, **kwargs):
        self._attr_value = self.get_value(record)


class ConstraintMessage(AttributeValidation):
    def fail_message(self, *args, **kwargs):
        failed_record = args[0]
        return self.message.format(clean_value(failed_record[self.attribute]), self.constraint)


class FileNameValidation(FileValidation):
    message = ValidatorMessages.FILE_NAME_VALIDATION_FAILED

    def execute(self, df, **kwargs):
        file_path = os.path.basename(kwargs.get('file_path', ''))
        file_path_format = self.constraint
        self._failed_info = file_path

        return any([re.match(item, file_path) for item in file_path_format])

    def fail_message(self, *args, **kwargs):
        return self.message.format(self.failed_info(), self.constraint)


class FileTypeValidation(FileValidation):
    message = ValidatorMessages.FILE_EXTN_VALIDATION_FAILED

    def execute(self, df, **kwargs):
        file_path = kwargs.get('file_path', '')
        file_extn_format = self.constraint
        self._failed_info = file_path

        return any([True if extn in file_path else False for extn in file_extn_format])

    def fail_message(self, *args, **kwargs):
        return self.message.format(self.failed_info(), self.constraint)


class HeaderValidation(FileValidation):
    message = ValidatorMessages.HEADER_VALIDATION_FAILED_WITH_MISSING_COLUMN

    def execute(self, df, **kwargs):
        required_columns = self.constraint

        if not required_columns:
            return True

        columns = df.columns.values.tolist()
        if sorted(columns) == sorted(required_columns):
            return True

        missing_columns = set(required_columns).difference(set(columns))
        if len(missing_columns) == 0:
            return True

        self._failed_info = missing_columns

        return False

    def fail_message(self, *args, **kwargs):
        return self.message.format(self.failed_info())


class DataTypeAttributeValidation(AttributeValidation):
    tags = ["Attribute", "Data Type"]

    def execute(self, record, **kwargs):
        super(DataTypeAttributeValidation, self).execute(record, **kwargs)
        return type(self._attr_value) in kwargs.get('data_type')


class IsStringAttributeValidation(DataTypeAttributeValidation):
    def execute(self, record, **kwargs):
        kwargs.update({"data_type": [str]})
        return super(IsStringAttributeValidation, self).execute(record, **kwargs)


class IsNullAttributeValidation(AttributeValidation):
    def execute(self, record, **kwargs):
        super(IsNullAttributeValidation, self).execute(record, **kwargs)
        return not empty(self._attr_value)


class RequiredAttributeValidation(AttributeValidation):
    def execute(self, record, **kwargs):
        super(RequiredAttributeValidation, self).execute(record, **kwargs)
        return required(self._attr_value)


class IsDateAttributeValidation(AttributeValidation):
    def execute(self, record, **kwargs):
        super(IsDateAttributeValidation, self).execute(record, **kwargs)
        return is_date(self._attr_value)


class AttributeLengthValidation(AttributeValidation):
    def execute(self, record, **kwargs):
        super(AttributeLengthValidation, self).execute(record, **kwargs)
        return self.constraint[0] <= len(self._attr_value) <= self.constraint[1]

    def fail_message(self, *args, **kwargs):
        failed_record = args[0]
        return self.message.format(self.attribute, self.constraint, clean_value(failed_record[self.attribute]))


class RegexAttributeValidation(ConstraintMessage):
    def execute(self, record, **kwargs):
        super(RegexAttributeValidation, self).execute(record, **kwargs)
        return any([re.match(regex, self._attr_value) for regex in self.constraint])


class EnumAttributeValidation(ConstraintMessage):
    def execute(self, record, **kwargs):
        super(EnumAttributeValidation, self).execute(record, **kwargs)
        return self._attr_value in self.constraint


class DateFormatAttributeValidation(ConstraintMessage):
    def execute(self, record, **kwargs):
        super(DateFormatAttributeValidation, self).execute(record, **kwargs)
        return is_date(self._attr_value, self.constraint)


class AlphaNumericAttributeValidation(RegexAttributeValidation):
    def execute(self, record, **kwargs):
        self.constraint = ["^[A-Za-z0-9]+$"]
        return super(AlphaNumericAttributeValidation, self).execute(record, **kwargs)

    def fail_message(self, *args, **kwargs):
        failed_record = args[0]
        return self.message.format(clean_value(failed_record[self.attribute]))


class UniqueAttributeValidation(AttributeValidation):
    def execute(self, record, **kwargs):
        super(UniqueAttributeValidation, self).execute(record, **kwargs)
        attr = self.attribute
        # df[df.attr == self._attr_value].index.tolist()
        # return self._attr_value in getattr(df, self.attribute).tolist()
        # df[df.test2 == 8].index.tolist()
        # return getattr(df, self.attribute).tolist() == list(getattr(df, self.attribute).unique())
