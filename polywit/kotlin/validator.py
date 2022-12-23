from polywit.base import Validator, FileProcessor, WitnessProcessor, TestHarness
from polywit.kotlin import KotlinFileProcessor, KotlinWitnessProcessor, KotlinTestHarness


class KotlinValidator(Validator):
    def __init__(self, config, directory=None):
        """
        The constructor of Validator collects information of output directory is specified
        :param directory: Directory that the test harness will be written to.
        """
        super().__init__(config, directory=directory)
        self._file_processor = KotlinFileProcessor(
            self.directory,
            self.config['benchmark'],
            self.config['package_paths']
        )
        self._witness_processor = KotlinWitnessProcessor(
            self.directory,
            self.config['witness_file']
        )
        self._test_harness = KotlinTestHarness(self.directory)

    @property
    def file_processor(self) -> FileProcessor:
        return self._file_processor

    @property
    def witness_processor(self) -> WitnessProcessor:
        return self._witness_processor

    @property
    def test_harness(self) -> TestHarness:
        return self._test_harness
