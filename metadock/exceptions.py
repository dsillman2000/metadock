class MetadockException(Exception):
    pass


class MetadockProjectException(MetadockException):
    pass


class MetadockTemplateParsingException(MetadockException):
    pass


class MetadockContentSchematicParsingException(MetadockException):
    pass


class MetadockYamlImportError(MetadockException):
    pass
