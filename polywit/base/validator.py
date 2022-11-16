"""
 This file is part of polywit, a poly-language execution-based violation-witness validator
 https://github.com/polywit/polywit.

 This module deals with the base building of the test harness
"""
import tempfile
from abc import ABC, abstractmethod
from typing import List

from polywit.base import WitnessProcessor, FileProcessor
from polywit.utils import filter_assumptions
from polywit.base import TestHarness, PolywitTestResult


class Validator(ABC):
    """
    The class Validator gives functionality for processing the input files,
    constructing, executing the test harness and reporting the result
    """

    def __init__(self, config, directory=None):
        """
        The constructor of Validator collects information of output directory is specified
        :param directory: Directory that the test harness will be written to.
        """
        self.directory = tempfile.mkdtemp() if directory is None else directory
        self.config = config

    @property
    @abstractmethod
    def file_processor(self) -> FileProcessor:
        pass

    @property
    @abstractmethod
    def witness_processor(self) -> WitnessProcessor:
        pass

    @property
    @abstractmethod
    def test_harness(self) -> TestHarness:
        pass

    def preprocess(self) -> None:
        """
        Run the preprocessing steps for the processors
        """
        self.file_processor.preprocess()
        self.witness_processor.preprocess()

    def extract_assumptions(self) -> List[str]:
        """
        Extracts the assumptions from the witness file

        :return: List of assumptions
        """
        position_type_map = self.file_processor.extract_position_type_map()
        assumptions = self.witness_processor.extract_assumptions()
        return filter_assumptions(position_type_map, assumptions)

    def execute_test_harness(self, assumptions: List[str]) -> PolywitTestResult:
        self.test_harness.build_test_harness(assumptions)
        return self.test_harness.run_test_harness()
