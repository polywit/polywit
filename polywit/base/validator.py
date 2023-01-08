"""
 This file is part of polywit, a poly-language execution-based violation-witness validator
 https://github.com/polywit/polywit.

 This module deals with the base building of the test harness
"""
import tempfile
from abc import ABC, abstractmethod
from textwrap import indent
from typing import List

from tabulate import tabulate
from halo import Halo

from polywit.base import WitnessProcessor, FileProcessor
from polywit._typing import Assumption, Position
from polywit.utils import filter_assumptions
from polywit.base import TestHarness, PolywitTestResult


class Validator(ABC):
    """
    The class Validator gives functionality for processing the input files,
    constructing, executing the test harness and reporting the result
    """

    PREPROCESS_BENCHMARK_MESSAGE = 'Preprocessing benchmark files'
    PREPROCESS_WITNESS_MESSAGE = 'Preprocessing witness file'
    EXTRACT_POS_TYPE_MAP_MESSAGE = 'Extracting position type map from benchmarks'
    EXTRACT_ASSUMPTIONS_MESSAGE = 'Extracting assumptions from witness'
    BUILD_TEST_HARNESS_MESSAGE = 'Building test harness'
    RUN_TEST_HARNESS_MESSAGE = 'Executing test harness'

    def __init__(self, config, directory=None):
        """
        The constructor of Validator collects information of output directory is specified
        :param directory: Directory that the test harness will be written to.
        """
        self.directory = tempfile.mkdtemp() if directory is None else directory
        self.config = config
        self.spinner = Halo(text='', spinner='dots')

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
        self.spinner.start(self.PREPROCESS_BENCHMARK_MESSAGE)
        self.file_processor.preprocess()
        self.spinner.succeed()

        self.spinner.start(self.PREPROCESS_WITNESS_MESSAGE)
        self.witness_processor.preprocess()
        self.spinner.succeed()

    def extract_assumptions(self) -> List[Assumption]:
        """
        Extracts the assumptions from the witness file

        :return: List of assumptions
        """

        self.spinner.start(self.EXTRACT_POS_TYPE_MAP_MESSAGE)
        position_type_map = self.file_processor.extract_position_type_map()
        self.spinner.succeed()

        self.spinner.start(self.EXTRACT_ASSUMPTIONS_MESSAGE)
        assumptions = self.witness_processor.extract_assumptions()
        self.spinner.succeed()

        assumptions = filter_assumptions(position_type_map, assumptions)
        if self.config['show_assumptions']:
            self._print_assumptions(assumptions, position_type_map)
        return assumptions

    def execute_test_harness(self, assumptions: List[Assumption]) -> PolywitTestResult:

        self.spinner.start(self.BUILD_TEST_HARNESS_MESSAGE)
        self.test_harness.build_test_harness(assumptions)
        self.spinner.succeed()

        self.spinner.start(self.RUN_TEST_HARNESS_MESSAGE)
        result = self.test_harness.run_test_harness()
        self.spinner.succeed()

        return result

    @staticmethod
    def _print_assumptions(assumptions: List[Assumption], position_type_map: dict[Position, str]):
        headers = ['Position', 'Value', 'Type']
        table_data = []
        for assumption in assumptions:
            position = assumption[0]
            formatted_position = f'{position[0]}:{position[1]}'
            value = assumption[1]
            value_type = position_type_map[position]
            table_data.append((formatted_position, value, value_type))
        # Create table and indent by 2 spaces to look nice
        print(indent(tabulate(table_data, headers=headers, tablefmt="pretty"), '  '))
