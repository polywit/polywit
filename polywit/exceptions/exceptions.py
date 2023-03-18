class ValidationError(Exception):
    def __init__(self, phase):
        self.message = f'Polywit has encountered an issue during {phase}.'
        self.retry_message = 'Retry using --stacktrace to see the full stacktrace.'
        super().__init__(self.message)


class WitnessProcessorError(ValidationError):
    def __init__(self, phase="witness processing"):
        super().__init__(phase)


class WitnessPreprocessingError(WitnessProcessorError):
    PHASE = 'witness preprocessing'

    def __init__(self):
        super().__init__(WitnessPreprocessingError.PHASE)


class AssumptionExtractionError(WitnessProcessorError):
    PHASE = 'assumption extraction'

    def __init__(self):
        super().__init__(AssumptionExtractionError.PHASE)


class FileProcessorError(ValidationError):
    def __init__(self, phase="file processing"):
        super().__init__(phase)


class FilePreprocessingError(FileProcessorError):
    PHASE = 'file preprocessing'

    def __init__(self):
        super().__init__(FilePreprocessingError.PHASE)


class PositionTypeExtractionError(WitnessProcessorError):
    PHASE = 'position type extraction'

    def __init__(self):
        super().__init__(AssumptionExtractionError.PHASE)


class TestHarnessError(ValidationError):
    def __init__(self, phase='test harness development'):
        super().__init__(phase)


class TestHarnessExecutionError(TestHarnessError):
    PHASE = 'execution of test harness'

    def __init__(self):
        super().__init__(TestHarnessExecutionError.PHASE)


class TestHarnessConstructionError(TestHarnessError):
    PHASE = 'construction of test harness'

    def __init__(self):
        super().__init__(TestHarnessConstructionError.PHASE)
