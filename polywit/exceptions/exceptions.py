class ValidationException(Exception):
    pass


class WitnessProcessorException(ValidationException):
    pass


class FileProcessorException(ValidationException):
    pass


class TestHarnessException(ValidationException):
    pass
