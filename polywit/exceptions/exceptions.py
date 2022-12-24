class ValidationError(Exception):
    pass


class WitnessProcessorError(ValidationError):
    pass


class WitnessFormatError(WitnessProcessorError):
    pass


class FileProcessorError(ValidationError):
    pass


class TestHarnessError(ValidationError):
    pass
