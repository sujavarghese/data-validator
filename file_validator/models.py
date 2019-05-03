from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
import json
import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
)

Base = declarative_base()


class Status(object):
    failed = "FAILED"
    validated = "VALIDATED"
    validating = "VALIDATING"


class ValidationRecord(Base):
    __tablename__ = 'validation_record'
    __table_args__ = {
        'mysql_charset': 'utf8',
        'mysql_collate': 'utf8_unicode_ci',
    }

    def __repr__(self):
        return "<ValidationRecord(name='%s' on input file='%s' started at='%s', status='%s')>" % (
            self.name, self.input_path, self.started_at, self.status)

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    ended_at = Column(DateTime, nullable=True)
    name = Column(String(512), nullable=True)
    input_path = Column(String(512), nullable=False)
    status = Column(String(12), nullable=True)
    _logs = Column('logs', Text, nullable=True)
    _output_path = Column('output_path', Text, nullable=True)
    _summary = Column('summary', Text, nullable=True)
    _detailed = Column('detailed', Text, nullable=True)

    @hybrid_property
    def logs(self):
        return json.loads(self._logs)

    @logs.setter
    def logs(self, logs):
        self._logs = json.dumps(logs)

    @hybrid_property
    def output_path(self):
        return json.loads(self._output_path)

    @output_path.setter
    def output_path(self, path):
        self._output_path = json.dumps(path)

    @hybrid_property
    def summary(self):
        return json.loads(self._summary)

    @summary.setter
    def summary(self, summary):
        self._summary = summary

    @hybrid_property
    def detailed(self):
        return json.loads(self._detailed)

    @detailed.setter
    def detailed(self, detailed):
        self._detailed = detailed


class Meta:
    model = ValidationRecord

