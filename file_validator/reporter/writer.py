import pandas as pd
import os.path

EXCEL = 'xlsx'
CSV = 'csv'
PDF = 'pdf'


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

        report.summary().to_csv(self.summary_path, index=False, mode='w')
        report.detailed().to_csv(self.detailed_path, index=False, mode='w')


class ExcelReportWriter(ReportWriter):
    def write(self, report, op_type=EXCEL, **kwargs):
        super(ExcelReportWriter, self).write(report, op_type, **kwargs)

        report_path = kwargs.get("report_path")
        self.summary_path = os.path.join(report_path, kwargs.get("report_name"))
        self.detailed_path = self.summary_path
        summary_report_name = kwargs.get("summary_name", "Summary Report")
        detailed_report_name = kwargs.get("detailed_name", "Detailed Report")

        with pd.ExcelWriter(self.summary_path) as writer:
            report.summary().to_excel(writer, index=False, sheet_name=summary_report_name)
            report.detailed().to_excel(writer, index=False, sheet_name=detailed_report_name)


class JsonReportWriter(ReportWriter):
    def write(self, report, op_type=EXCEL, **kwargs):
        super(JsonReportWriter, self).write(report, op_type, **kwargs)

        report_path = kwargs.get("report_path")
        self.summary_path = os.path.join(report_path, kwargs.get("summary_name"))
        self.detailed_path = os.path.join(report_path, kwargs.get("detailed_name"))

        report.summary().to_json(self.summary_path, index=False, mode='a')
        report.detailed().to_json(self.detailed_path, orient='index', index=False)


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
