Key 1: fields
List of all columns that you plan to validate from input file. If you miss one column here, that will not be validated.
This list act as a basic check that ensure, you know which all columns you are validating.

Key 2: validations
A list of all validations you want to execute for the input file.
Every single item in this group will have a unique key called "validate_key". The validation rules mapped to this key
as complex array.
For eg, "file_name" is a validate_key that intend to validate file names when the matching regular expression is given.
The validation rules and attributes mapped to validate_key. It contains mandatory as well as optional fields.

tags: (Mandatory, List) Category to which the rule belongs to. Generic categories are "File Structure",  "Data",
"Naming" etc. Tags are used for validation reporting.

attributes: (Mandatory, List) Column names on which rules are applied. It can have pre-defined values such as "FILE"
(means rule is applicable on the file. Not on the attributes), "ALL" (means rule is applied on all columns)

constraint: (Optional, List) Any particular constraint that you want to customize. Constraints can be string of regex
or list of enumerals. The validation is suppose to handle varying data type and content.

pre-validation: (Optional, List) Apply custom logic before validating the record.

message: (Optional) The default message would be "XYZValidation failed for attribute <column1>". You can customise this
message here. Make sure you supply args by customising "fail_message()".

allow_multiple_config: (Optional) When a single validation type applied on with different constraints/messages/tags on
attributes, we need to nest configurations. For eg, "attribute_length" validation can be applied on multiple
attributes, with varying constraints. One attribute may expect length should be between 1 and 15 whereas other column
expect length between 5 and 10. In such scenarios, set value "true" here.

configs: This is the nested config for multiple constraints on same rule. Expects a list of attributes, constraints,
tags and custom messages. Here attribute is a mandatory column whereas tags, message and constraints are optional.
Optional columns will be inherited from the parent.

configs.tags: Same as tags

configs.attributes: Same as attributes

configs.constraint: Same as constraints

configs.message: Same as messages

configs.pre-validation: Same as messages


changes required per file,
schema json, schema/subschema, custom validations

Single,
call schema execution class, call reporting class, reporting, summary format