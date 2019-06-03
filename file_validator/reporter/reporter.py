from collections import defaultdict
from datetime import datetime
import pandas as pd

from file_validator.helper.utils import clean_value
from file_validator.messages import MessageMapping


class Base(object):
    def __init__(self, message_map=MessageMapping):
        self._summary = pd.DataFrame([], [])
        self._detailed = pd.DataFrame([], [])
        self.message_map = message_map()

    def report(self, schema, logs, **kwargs):
        log_status = self.find_log_status(logs, **kwargs)

        if log_status is False:
            self._summary = self.logs(logs)
            return log_status

        self._detailed = self.validation_result(schema, **kwargs)
        self._summary = self.prepare_summary(schema, **kwargs)
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
    def logs(logs):
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

    def detailed_columns(self):
        raise NotImplementedError()

    def validation_result(self, schema, **kwargs):
        raise NotImplementedError()

    def prepare_summary(self, schema, **kwargs):
        raise NotImplementedError()

    def write_into_db(self, validation_record):
        raise NotImplementedError()


class Report(Base):
    def prepare_summary(self, schema, **kwargs):
        def create_row(df, row):
            return df.append(row, ignore_index=True)

        def add_empty_row(df):
            return create_row(df, {"Summary": "", "Details": ""})

        df = pd.DataFrame(columns=["Summary", "Details"])
        df = create_row(df, {"Summary": "File path", "Details": kwargs.get("file_path")})
        df = create_row(df, {"Summary": "File Type", "Details": schema.schema_type})
        df = create_row(df, {"Summary": "Ran at", "Details": datetime.now()})
        df = create_row(df, {"Summary": "Validated Attributes", "Details": schema.fields()})
        df = create_row(df, {"Summary": "Total Number of Records", "Details": kwargs.get("records_count")})

        df = add_empty_row(df)
        df = create_row(df, {"Summary": "Rule Summary", "Details": ""})
        df = add_empty_row(df)

        summarise_rules = defaultdict(list)

        for rule in schema.schema():
            summarise_rules[self.message_map.get_id(rule)].append(rule)

        for rule_id, rules in summarise_rules.items():
            pass_count = 0
            fail_count = 0
            for rule in rules:
                pass_count += len(rule.passed_objects())
                fail_count += len(rule.failed_objects())

            if fail_count > 0:
                df = create_row(df, {
                    "Summary": str(rule_id) + ": Failures",
                    "Details": fail_count})
                df = create_row(df, {
                    "Summary": str(rule_id) + ": Passes",
                    "Details": pass_count})
        return df

    def detailed_columns(self):
        return [
            "Rule ID", "Category", "Sub Category", "Type", "Unique ID", "Attribute", "Value", "Fail Message",
            # "Rule Name",
        ]

    def prepare_row(self, df, rule, rule_id, category, typ, sub_category, columns, failed_record=None, **kwargs):
        unique_id = kwargs.get("file_path", 'FILE') if rule.is_file_rule else clean_value(failed_record[rule.unique_key])
        attr_value = "N/A" if rule.is_file_rule else clean_value(failed_record[rule.attribute])
        message = rule.fail_message() if rule.is_file_rule else rule.fail_message(failed_record, **kwargs)

        values = {
            "Rule ID": rule_id,
            # "Rule Name": rule_name,
            "Category": category,
            "Type": typ,
            "Sub Category": sub_category,
            "Unique ID": unique_id,
            "Attribute": rule.attribute,
            "Value": attr_value,
            # "Constraints": rule.constraint,
            "Fail Message": message
        }
        self.length_check(columns, values)
        return df.append(values, ignore_index=True)

    def length_check(self, c_list, v_list):
        if len(c_list) != len(v_list):
            raise Exception("Columns and rows have different number of items. "
                            "Please confirm mapping again.")

    def validation_result(self, schema, **kwargs):
        columns = self.detailed_columns()
        df = pd.DataFrame(columns=columns)

        schema_type = schema.schema_type
        for rule in schema.schema():
            rule_id = self.message_map.get_id(rule)
            category = rule.tags[0]
            sub_category = rule.tags[1] if len(rule.tags) > 1 else None
            passed = rule.failed_objects().empty

            if not passed:
                if rule.is_file_rule:
                    df = self.prepare_row(df, rule, rule_id, category, schema_type, sub_category, columns, None, **kwargs)
                else:
                    for key, failed_record in rule.failed_objects().iterrows():
                        df = self.prepare_row(df, rule, rule_id, category, schema_type, sub_category, columns, failed_record, **kwargs)

        return df

    def write_into_db(self, validation_record):
        from file_validator.models import Status
        validation_record.status = Status.validated
        validation_record.ended_at = datetime.now()
        validation_record.summary = self.summary().to_json()
        validation_record.detailed = self.detailed().to_json()
        return validation_record
