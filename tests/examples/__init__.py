from file_validator.schema.schema import *
from file_validator.schema.generator import *
from file_validator.validator.validator import *
from file_validator.validator.rules import *
from file_validator.reader import *
from file_validator.reporter import *
from file_validator.models import *
from file_validator.validator.utils import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging

logger = logging.getLogger()


class CustomRule(AttributeValidation):
    def execute(self, record, **kwargs):
        super(CustomRule, self).execute(record, **kwargs)
        return True


class Schema(FeatureSchema):
    map = {
        'check_xyz': CustomRule
    }


class CustomValidator(Validator):
    pass


class Getter(object):
    def get(self, filepath, extension, **kwargs):
        has_read, log, df = CSVFileReader().validate_and_read(filepath, extension, **kwargs)

        print(log.serialize())

        if has_read:
            return df, log
        return None, log


class Runner(object):
    def run(self, df, logs, schema_type, schema_path, **kwargs):
        schema_inst = SchemaFactory()
        schema_inst.generate(Schema,
            schema_type, schema_path, **kwargs)

        validator = CustomValidator(logs)
        schema, logs = validator(df, schema_inst.schema(), **kwargs)

        return schema, logs


class Reporter(object):
    def report(self, result, logs, records_count, **kwargs):
        report = Report()
        report.report(schema=result, logs=logs, records_count=records_count, **kwargs)

        writer = CSVReportWriter()
        writer.write(report, **kwargs)
        return writer


def main():
    db_connect_str = 'mysql+pymysql://sujavarghese:root@localhost/MARKETING_CLOUD?charset=utf8'
    engine = create_engine(db_connect_str, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    filepath = '/Users/sujavarghese/projects/file-validator/tests/fixtures/tbl_account_golden_gate_12020202020202.csv'
    extn = 'csv'
    schema_type = "KTAS-VEHICLE"
    schema_path = "/Users/sujavarghese/projects/file-validator/tests/fixtures/test_schema.json"
    report_path = "/Users/sujavarghese/projects/file-validator/tests/fixtures"
    report_name = "validation-report-{}.csv".format(schema_type)
    summary_name = "Summary Report {}.csv".format(schema_type)
    detailed_name = "Detailed Report {}.csv".format(schema_type)

    df, log = Getter().get(filepath, extn, as_dict=False, check_extn=False)

    validation_record = ValidationRecord(input_path=filepath, status=Status.validating)
    session.add(validation_record)
    session.commit()

    if not df.empty:
        result, log = Runner().run(df, log, schema_type=schema_type, schema_path=schema_path, file_path=filepath, data_type=extn)

        validation_record.name = schema_type
        validation_record.logs = log.serialize()
        session.commit()

        writer = Reporter().report(
            result, log, df.count()[0], report_path=report_path, report_name=report_name, summary_name=summary_name,
            detailed_name=detailed_name, file_path=filepath, data_type=extn
        )

        validation_record.output_path = {'detailed': writer.detailed_path, 'summary': writer.summary_path}
        validation_record.status = Status.validated
        validation_record.ended_at = datetime.now()
        validation_record.summary = writer.summary_json
        validation_record.detailed = writer.detailed_json
        session.commit()

    filepath = '/Users/sujavarghese/projects/file-validator/tests/fixtures/tbl_contact_golden_gate_12020202020202.csv'
    schema_type = "KTAS-CONTACT"
    extn = 'csv'
    summary_name = "Summary Report {}.csv".format(schema_type)
    detailed_name = "Detailed Report {}.csv".format(schema_type)

    df, log = Getter().get(filepath, extn, as_dict=False, check_extn=False)

    validation_record = ValidationRecord(input_path=filepath, status=Status.validating)
    session.add(validation_record)
    session.commit()

    if not df.empty:
        result, log = Runner().run(df, log, schema_type=schema_type, schema_path=schema_path, file_path=filepath, data_type=extn)

        validation_record.name = schema_type
        validation_record.logs = log.serialize()
        session.commit()

        writer = Reporter().report(
            result, log, df.count()[0], report_path=report_path, report_name=report_name, summary_name=summary_name,
            detailed_name=detailed_name, file_path=filepath, data_type=extn
        )

        validation_record.output_path = {'detailed': writer.detailed_path, 'summary': writer.summary_path}
        validation_record.status = Status.validated
        validation_record.ended_at = datetime.now()
        validation_record.summary = writer.summary_json
        validation_record.detailed = writer.detailed_json
        session.commit()
        session.close()


if __name__ == "__main__":
    main()

    table_creation_script = """
    CREATE TABLE `validation_record` (
      `id` int NOT NULL AUTO_INCREMENT,
      `started_at` datetime NOT NULL,
      `ended_at` datetime DEFAULT NULL,
      `name` varchar(512) DEFAULT NULL,
      `input_path` varchar(512) NOT NULL,
      `output_path` text DEFAULT NULL,
      `status` varchar(12) DEFAULT NULL,
      `logs` text DEFAULT NULL,
      `summary` text DEFAULT NULL,
      `detailed` text DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """
