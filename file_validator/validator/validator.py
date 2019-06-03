import pandas as pd
import logging
from file_validator.validator.utils import *

logger = logging.getLogger()


class Base(object):
    def __init__(self, logs):
        self._status = True
        self.log = logs

    def __call__(self, *args, **kwargs):
        return self._run(*args, **kwargs)

    def _run(self, *args, **kwargs):
        df = args[0]
        schema = args[1]
        df, schema = self.pre_validate(df, schema, **kwargs)
        df, schema = self._validate(df, schema, **kwargs)
        return self.post_validate(df, schema, **kwargs)

    def pre_validate(self, df, schema, **kwargs):
        """
        Perform actions on DF, prior to validation. Could include data clean up etc.
        :param df:
        :param schema:
        :param kwargs:
        :return:
        """
        raise NotImplementedError()

    def post_validate(self, df, schema, **kwargs):
        """
        Perform action on DF, post validation. Could include logging etc.
        :param df:
        :param schema:
        :param kwargs:
        :return:
        """
        raise NotImplementedError()

    def _validate(self, df, schema, **kwargs):
        """
        Perform validation here
        :param df:
        :param schema:
        :param kwargs:
        :return:
        """
        raise NotImplementedError()


class FileValidator(Base):
    pass


class AttributeValidator(Base):
    pass


class Validator(AttributeValidator, FileValidator):
    def post_validate(self, df, schema, **kwargs):
        return schema, self.log

    def pre_validate(self, df, schema, **kwargs):
        return df, schema

    def _validate(self, df, schema, **kwargs):
        """
        Run validations one by one. Iterate through the list of validations and apply
        1. pre validation rules 2. constraint 3. validation rule
        Get the failed as well as passed objects and process them.
        :param df:
        :param schema:
        :param kwargs:
        :return:
        """
        schema_fields = schema.fields()

        ignored_columns = [col for col in df.columns if col not in schema_fields]
        logger.info('Source columns {} will be ignored.'.format(ignored_columns))

        for rule in schema.validations():
            logger.info("Starting Rule {}" .format(rule.name()))
            try:
                result_df = self._validate_rule(
                    self.apply_pre_validation_correction(df, rule, **kwargs), rule, **kwargs)
                self._post_validate_rule(result_df, df, rule, **kwargs)
            except Exception as e:
                logger.info("Failed Rule {}. {}".format(rule.name(), e))
            logger.info("Ending Rule {}".format(rule.name()))

        return df, schema

    def apply_pre_validation_correction(self, df, rule, **kwargs):
        """
        Execute the pre validation rules. This could be clean up or
        :param df:
        :param rule:
        :param kwargs:
        :return:
        """
        pre_validation = rule.pre_validation
        if not pre_validation:
            self.log.record(rule.name(), "No pre validation applied.".format(rule.attribute), True)
            return df

        if isinstance(pre_validation, str):
            pre_validation = [pre_validation]

        for action in pre_validation:
            global_func = globals().get(action, None)
            if global_func:
                df[rule.attribute] = df[rule.attribute].apply(lambda x: global_func(x))
            else:
                df[rule.attribute] = df[rule.attribute].apply(action)

        self.log.record(rule.name(), "Pre validation applied on {} successfully.".format(rule.attribute), True)
        return df

    def apply_constraints(self, df, rule, **kwargs):
        """
        :param df:
        :param rule:
        :param kwargs:
        :return:
        """
        constraint = rule.constraint
        if not (constraint and isinstance(constraint, list)):
            self.log.record(rule.name(), "No constraint applied.", True)

        return df

    def _validate_rule(self, df, rule, **kwargs):
        """
        :param df:
        :param rule:
        :param kwargs:
        :return:
        """
        df = self.apply_constraints(df, rule, **kwargs)
        if rule.is_file_rule:
            result_df = pd.DataFrame({rule.name(): rule._execute(df, **kwargs)}, index=[rule.name()])
        else:
            result_df = pd.DataFrame(df[rule.attribute].apply(rule._execute, **kwargs))
        result_df = result_df.rename(columns={result_df.columns[0]: rule.name()})

        self.log.record(rule.name(), "Validated field {}.".format(rule.attribute), all(result_df[rule.name()]))
        return result_df

    def _post_validate_rule(self, result_df, df, rule, **kwargs):
        if not rule.is_file_rule:
            result_df = pd.concat([df[rule.unique_key[0]], df[rule.attribute], result_df], axis=1)

        rule.process_result(result_df)

