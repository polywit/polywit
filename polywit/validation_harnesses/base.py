"""
 This file is part of polywit, a poly-language execution-based violation-witness validator
 https://github.com/polywit/polywit.

 This module deals with the base building of the validation harness
"""

import os
import subprocess
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Tuple


class BaseValidationHarness(ABC):
    """
    The class BaseValidationHarness gives base functionality and definitions for
    all the tests creation and compilation of the validation harness
    """

    def __init__(self, directory):
        """
        The constructor of BaseValidationHarness collects information on the 
        output directory
        :param directory: Directory that the harness will write to
        """
        self.directory = directory
        self.validation_path = os.path.join(
            self.directory,
            'Verifier'
        )
        self.test_path = os.path.join(
            self.directory,
            'Test'
        )
        self.run_args = []

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
    def _write_data(path: str, data:  List[str]) -> None:
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
        :param command: List of seperated command to run
        :return: stdout and stderr from command
        """
        with subprocess.Popen(command,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            proc.wait()
            out = proc.stdout.read().decode("utf-8")
            err = proc.stderr.read().decode("utf-8")
        return out, err

    def build_validation_harness(self, assumptions) -> None:
        """
         Constructs and compiles the validation harness consisting of
         the unit test and the test validation
        :param assumptions: Assumptions extracted from the witness
        """
        self._build_unit_test()
        self._build_test_verifier(assumptions)

    @abstractmethod
    def _build_unit_test(self) -> None:
        """
        Constructs the unit tests from Test.java
        """

    @abstractmethod
    def _build_test_verifier(self, assumptions) -> None:
        """
        Constructs the tests verifier from a list of assumptions
        and Verifier.java
        :param assumptions: Assumptions extracted from the witness
        """

    def run_validation_harness(self) -> str:
        """
        Runs the validation harness and reports the outcome of the validation execution
        :return: The validation result
        """
        out, err = self._run_command(self.run_args)
        return self._parse_validation_result(out, err)

    @abstractmethod
    def _parse_validation_result(self, validation_output, validation_error) -> None:
        """
        Parses the validation result and returns appropriate message
        :param validation_output: Stdout from validation run
        :param validation_error: Stderr from validation run
        """

class ValidationResult(Enum):
    CORRECT = "Witness correct", "\033[92m"
    SPURIOUS = "Witness spurious", "\033[91m"
    UNKNOWN = "Witness could not be validated", "\033[93m"
    def __new__(cls, *args, **kwds):
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

