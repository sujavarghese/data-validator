import pandas as pd
from collections import defaultdict


class LoggerMixin:
    def carry_forward_log(self):
        return self.log


class LogRecordFactory(object):

    def __init__(self, records=defaultdict(list)):
        if (
                isinstance(records, pd.DataFrame) and records.empty
        ) or (
                not(isinstance(records, pd.DataFrame) and not records)
        ):
            self._records = defaultdict(list)
        else:
            self._records.update(records)

    def record(self, name, msg, status):
        record = LogRecord(name, msg, status)
        self._records[name].append(record)

    def get_records(self):
        return self._records

    def get_records_by(self, name):
        self.get_records().get(name, [])

    def serialize(self, clear=False):
        logs = [
            (name, str(log))
            for name, logs in self.get_records().items()
            for log in logs
        ]
        if clear:
            self._clear()

        return logs

    def _clear(self):
        self._records = defaultdict(list)


class LogRecord(object):
    def __init__(self, name, msg, status):
        self.name = name
        self.msg = msg
        self.status = status

    def __str__(self):
        return '<LogRecord: name={}, status={}, message={}>'.format(self.name, self.status, self.msg)

    __repr__ = __str__

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_message(self):
        return self.msg

    def set_message(self, msg):
        self.msg = msg

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status


Logger = LogRecordFactory
