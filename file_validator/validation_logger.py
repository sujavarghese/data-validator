import pandas as pd


class ValidatorLogMixin:
    def carry_forward_log(self):
        return self.log


class ValidationRecordFactory(object):

    def __init__(self, records=pd.DataFrame([])):
        if (
                isinstance(records, pd.DataFrame) and records.empty
        ) or (
                not(isinstance(records, pd.DataFrame) and not records)
        ):
            self._records = pd.DataFrame([])
        else:
            self._records.update(records)

    def make_record(self, unique_name, msg, status):
        record = ValidationRecord(unique_name, msg, status)
        self._records[unique_name].append(record)

    def get_records(self):
        return self._records

    def get_records_by(self, name):
        self.get_records().get(name, [])


class ValidationRecord(object):
    def __init__(self, name, msg, status):
        self.name = name
        self.msg = msg
        self.status = status

    def __str__(self):
        return '<ValidationRecord: {}, {}, {}">'.format(self.name, self.status, self.msg)

    def get_message(self):
        return self.msg

    def set_message(self, msg):
        self.msg = msg

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status


Log = ValidationRecordFactory
