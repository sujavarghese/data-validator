import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from file_validator.schema.generator import *
from file_validator.reader import *
from file_validator.reporter import *
from file_validator.models import *
from file_validator.validator.utils import *

from tests.examples.ktas_csv_contacts_list.schema import ContactsSchema
from tests.examples.ktas_csv_contacts_list.validator import CustomValidator, MessageMap


logger = logging.getLogger()


class Reader(object):
    def get(self, filepath, extension, **kwargs):
        has_read, log, df = CSVFileReader().validate_and_read(filepath, extension, **kwargs)

        print(log.serialize())

        if has_read:
            return df, log
        return None, log


class Runner(object):
    def run(self, df, logs, schema_type, schema_path, **kwargs):
        schema_inst = SchemaFactory()
        schema_inst.generate(ContactsSchema, schema_type, schema_path, **kwargs)
        validator = CustomValidator(logs)
        schema, logs = validator(df, schema_inst.schema(), **kwargs)

        return schema, logs


class Reporter(object):
    def report(self, result, logs, records_count, **kwargs):
        report = Report(message_map=MessageMap)
        report.report(schema=result, logs=logs, records_count=records_count, **kwargs)

        writer = CSVReportWriter()
        writer.write(report, **kwargs)
        return writer


def main():
    db_connect_str = 'mysql+pymysql://sujavarghese:root@localhost/MARKETING_CLOUD?charset=utf8'
    engine = create_engine(db_connect_str, echo=False)

    Session = sessionmaker(bind=engine)
    session = Session()

    [session.execute(sql) for sql in table_creation_scripts]
    session.commit()

    filepath = os.path.join(os.getcwd(), 'input', 'KTAS_CONTACTSLIST_IMPORT_DAILY_20190313230237.csv')
    extn = 'csv'
    schema_type = "KTAS-CONTACT"
    schema_path = os.path.join(os.getcwd(), 'input', 'ktas_contacts.json')
    report_path = os.path.join(os.getcwd(), 'reports')
    report_name = "validation-report-{}.csv".format(schema_type)
    summary_name = "Summary Report {}.csv".format(schema_type)
    detailed_name = "Detailed Report {}.csv".format(schema_type)

    df, log = Reader().get(filepath, extn, as_dict=False, check_extn=False)

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
    table_creation_scripts = [
        "DROP TABLE IF EXISTS CsvContactsList",
        """CREATE TABLE `CsvContactsList` (
          `customer_id` varchar(64) NOT NULL,
          `email_address` varchar(512) DEFAULT NULL,
          `email_permission` varchar(512) DEFAULT NULL,
          `postal_street_1` varchar(512) DEFAULT NULL,
          `postal_street_2` varchar(512) DEFAULT NULL,
          `state` varchar(512) DEFAULT NULL,
          `full_name` varchar(512) DEFAULT NULL,
          `first_name` varchar(512) DEFAULT NULL,
          `last_name` varchar(512) DEFAULT NULL,
          `phone_number` varchar(32) DEFAULT NULL,
          `business_name` varchar(512) DEFAULT NULL,
          `lst_paymt_type` varchar(512) DEFAULT NULL,
          `ktas_insur_cust` varchar(512) DEFAULT NULL,
          `postal_code` int(11) DEFAULT NULL,
          PRIMARY KEY (`customer_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;""",
        "DROP TABLE IF EXISTS validation_record",
        """CREATE TABLE `validation_record` (
          `id` int NOT NULL AUTO_INCREMENT,
          `started_at` datetime NOT NULL,
          `ended_at` datetime DEFAULT NULL,
          `name` varchar(512) DEFAULT NULL,
          `input_path` varchar(512) NOT NULL,
          `output_path` text DEFAULT NULL,
          `status` varchar(12) DEFAULT NULL,
          `logs` LONGTEXT DEFAULT NULL,
          `summary` LONGTEXT DEFAULT NULL,
          `detailed` LONGTEXT DEFAULT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        ]
    main()
