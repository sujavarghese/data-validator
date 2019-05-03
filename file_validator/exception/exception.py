class EmptySchemaException(Exception):
    pass


class InvalidSchemaException(Exception):
    pass


class SchemaMissingFieldsException(Exception):
    pass


class NotDeclaredValidationMappingException(Exception):
    pass


class NotDeclaredFieldsException(Exception):
    pass


class NotDeclaredUniqueFieldsException(Exception):
    pass
