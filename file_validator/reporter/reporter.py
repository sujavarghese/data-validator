import pandas as pd
import os.path


EXCEL = 'xlsx'
CSV = 'csv'
PDF = 'pdf'


class Base(object):
    def __init__(self):
        self._summary = pd.DataFrame([], [])
        self._detailed = pd.DataFrame([], [])

    def report(self, schema, logs, **kwargs):
        log_status = self.find_log_status(logs, **kwargs)

        if log_status is False:
            self._summary = self.report_logs(logs)
            return log_status

        self._detailed = self.report_validation_result(schema, **kwargs)
        self._summary = self.prepare_summary_report(schema, **kwargs)
        return log_status

    @staticmethod
    def find_log_status(logs, **kwargs):
        return all([
            log_record.get_status()
            for name, log_records in logs.get_records().items()
            for log_record in log_records
            if name == kwargs.get("file_path")
        ])

    @staticmethod
    def report_logs(logs):
        df = pd.DataFrame(columns=["Name", "Status", "Description"])
        [
            df.append({
                "Name": log_record.get_name(),
                "Status": log_record.get_status(),
                "Description": log_record.get_message()
            }, ignore_index=True)
            for name, log_records in logs.get_records().items()
            for log_record in log_records
        ]

        return df

    def summary(self):
        return self._summary

    def detailed(self):
        return self._detailed

    def detailed_report_columns(self):
        raise NotImplementedError()

    def report_validation_result(self, schema, **kwargs):
        raise NotImplementedError()

    def prepare_summary_report(self, schema, **kwargs):
        raise NotImplementedError()


class Report(Base):
    def prepare_summary_report(self, schema, **kwargs):
        from datetime import datetime

        def create_row(df, row):
            return df.append(row, ignore_index=True)

        def add_empty_row(df):
            return create_row(df, {"Summary": "", "Details": ""})

        df = pd.DataFrame(columns=["Summary", "Details"])
        df = create_row(df, {"Summary": "File path", "Details": kwargs.get("file_path")})
        df = create_row(df, {"Summary": "Ran at", "Details": datetime.now()})
        df = create_row(df, {"Summary": "Validated attributes", "Details": schema.fields()})
        df = create_row(df, {"Summary": "Total records", "Details": kwargs.get("records_count")})

        df = add_empty_row(df)
        df = add_empty_row(df)
        df = create_row(df, {"Summary": "Rule Summary", "Details": ""})
        for rule in schema.schema():
            df = create_row(df, {
                "Summary": rule.validate_key + "_on_" + rule.attribute + " Failure count",
                "Details": len(rule.failed_objects())})
            df = create_row(df, {
                "Summary": rule.validate_key + "_on_" + rule.attribute + " Pass count",
                "Details": len(rule.passed_objects())})
        return df

    def detailed_report_columns(self):
        return [
            "Rule ID", "Category", "Sub Category", "Unique ID", "Attribute", "Value", "Fail Message", "Constraints",
            "Rule Name",
        ]

    def report_validation_result(self, schema, **kwargs):
        def prepare_report_row(rule_id, rule_name, category, sub_category, id, attribute, attr_value, constraint, message):
            return {
                "Rule ID": rule_id,
                "Rule Name": rule_name,
                "Category": category,
                "Sub Category": sub_category,
                "Unique ID": id,
                "Attribute": attribute,
                "Value": attr_value,
                "Constraints": constraint,
                "Fail Message": message
            }

        df = pd.DataFrame(columns=self.detailed_report_columns())

        for rule in schema.schema():
            attribute = rule.attribute
            rule_id = rule.validate_key + "_on_" + attribute
            rule_name = rule.name()
            category = rule.tags[0]
            sub_category = rule.tags[1] if len(rule.tags) > 1 else None
            constraint = rule.constraint
            status = rule.failed_objects().empty

            if not status:
                if rule.is_file_rule:
                    df = df.append(prepare_report_row(rule_id, rule_name, category, sub_category,
                        kwargs.get("file_path", 'FILE'), attribute, "N/A", constraint, rule.fail_message()), ignore_index=True)
                else:
                    for key, failed_record in rule.failed_objects().iterrows():
                        df = df.append(prepare_report_row(rule_id, rule_name, category, sub_category,
                            failed_record[rule.unique_key], attribute, failed_record[attribute], constraint,
                            rule.fail_message(failed_record, **kwargs)), ignore_index=True)
        return df


class ReportWriter(object):
    summary_path = None
    detailed_path = None
    summary_json = None
    detailed_json = None

    def __init__(self):
        self.allowed_types = [EXCEL, CSV, PDF]

    def set_allowed_type(self, type):
        self.allowed_types.append(type)

    def write(self, report, op_type, **kwargs):
        if op_type not in self.allowed_types:
            raise Exception("{} is not an allowed output format. You need to create a writer and add it in the "
                            "allowed_types. The allowed_types are: {}".format(op_type, self.allowed_types))
        pd.set_option('display.max_colwidth', -1)
        self.summary_json = report.summary().to_json()
        self.detailed_json = report.detailed().to_json()


class CSVReportWriter(ReportWriter):
    def write(self, report, op_type=CSV, **kwargs):
        super(CSVReportWriter, self).write(report, op_type, **kwargs)

        report_path = kwargs.get("report_path")
        self.summary_path = os.path.join(report_path, kwargs.get("summary_name"))
        self.detailed_path = os.path.join(report_path, kwargs.get("detailed_name"))

        report.summary().to_csv(self.summary_path, index=False, mode='a')
        report.detailed().to_csv(self.detailed_path, index=False, mode='a')


class ExcelReportWriter(ReportWriter):
    def write(self, report, op_type=EXCEL, **kwargs):
        super(ExcelReportWriter, self).write(report, op_type, **kwargs)

        report_path = kwargs.get("report_path")
        self.summary_path = os.path.join(report_path, kwargs.get("report_name"))
        self.detailed_path = self.summary_path
        summary_report_name = kwargs.get("summary_name", "Summary Report")
        detailed_report_name = kwargs.get("detailed_name", "Detailed Report")

        with pd.ExcelWriter(self.summary_path) as writer:
            report.summary().to_excel(writer, sheet_name=summary_report_name)
            report.detailed().to_excel(writer, sheet_name=detailed_report_name)


class PDFReportWriter(ReportWriter):
    def write(self, report, op_type=PDF, **kwargs):
        super(PDFReportWriter, self).write(report, op_type, **kwargs)

        report_path = kwargs.get("report_path")
        self.summary_path = os.path.join(report_path, kwargs.get("summary_name"))
        self.detailed_path = os.path.join(report_path, kwargs.get("detailed_name"))

        summary_html = report.summary().to_html(
            notebook=True, index=False, na_rep="<br/>", border="border", table_id="summary", justify="left")
        detailed_html = report.detailed().to_html(notebook=True, index=False, na_rep="", table_id="detailed", justify="left")

        import pdfkit
        pdfkit.from_string(
            summary_html, self.summary_path,
            options={"--title": "Non Conformance Report - Summary", "header-left": "Non Conformance Report - Summary"})
        pdfkit.from_string(
            detailed_html, self.detailed_path,
            options={"--orientation": "Landscape", "--page-size": "A2", "--title": "Non Conformance Report",
                     "header-left": "Non Conformance Report", "--zoom": 1.5})
