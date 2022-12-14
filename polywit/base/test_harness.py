"""
 This file is part of polywit, a poly-language execution-based violation-witness validator
 https://github.com/polywit/polywit.

 This module deals with the base building of the test harness
"""

import os
import subprocess
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Tuple

from polywit._typing import Assumption


class PolywitTestResult(Enum):
    CORRECT = "Witness correct", "\033[92m"
    SPURIOUS = "Witness spurious", "\033[91m"
    UNKNOWN = "Witness could not be validated", "\033[93m"

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, colour: str = None):
        self._colour_ = colour

    def __str__(self):
        return f'{self.colour}{self.value}\033[0m'

    @property
    def colour(self):
        return self._colour_


class TestHarness(ABC):
    """
    The class TestHarness gives base functionality and definitions for
    all the tests creation and compilation of the test harness
    """

    def __init__(self, directory):
        """
        The constructor of TestHarness collects information on the
        output directory

        :param directory: Directory that the harness will write to
        """
        self.directory = directory

    @property
    @abstractmethod
    def test_path(self):
        pass

    @property
    @abstractmethod
    def compile_cmd(self):
        pass

    @property
    @abstractmethod
    def run_cmd(self):
        pass

    @staticmethod
    def _read_data(path: str) -> List[str]:
        """
        Handles reading data from a file
        :param path: Path of a file to read from
        :return: Content of file
        """
        with open(path, 'r', encoding='utf-8') as file:
            content = file.readlines()
        return content

    @staticmethod
    def _write_data(path: str, data: List[str]) -> None:
        """
        Handles writing data to a specific file
        :param path: Path of a file to write to
        :param data: Desired content of file
        """
        # Check if write will involve a non-existent subdirectory
        subdir = os.path.dirname(path)
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        with open(path, 'wt', encoding='utf-8') as file:
            file.writelines(data)

    @staticmethod
    def _run_command(command: List[str]) -> Tuple[str, str]:
        """
        Handles running commands in subprocess

        :param command: List of separated command to run
        :return: stdout and stderr from command
        """
        with subprocess.Popen(command,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            proc.wait()
            out = proc.stdout.read().decode("utf-8")
            err = proc.stderr.read().decode("utf-8")
        return out, err

    @abstractmethod
    def build_test_harness(self, assumptions: List[Assumption]) -> None:
        """
        Constructs and compiles the test harness
        """
        pass

    @abstractmethod
    def run_test_harness(self) -> PolywitTestResult:
        """
        Runs the test harness and reports the outcome of the test execution

        :return: The test result
        """

    @staticmethod
    def _parse_test_result(test_output: str,
                           test_error: str,
                           correct_output: str,
                           incorrect_output: str) -> PolywitTestResult:
        """
        Parses the test result and returns appropriate message

        :param test_output: Stdout from test run
        :param test_error: Stderr from test run
        :param correct_output: Output fragment expected from a correct violation
        :param incorrect_output: Output fragment expected from an incorrect violation

        :return: Formatted output
        """
        # Set output to be stderr if there is some erroneous output
        test_output = test_error if test_error else test_output
        if correct_output in test_output:
            result = PolywitTestResult.CORRECT
        elif incorrect_output in test_output:
            result = PolywitTestResult.SPURIOUS
        else:
            result = PolywitTestResult.UNKNOWN
        return result
