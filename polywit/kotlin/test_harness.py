"""
 This file is part of polywit, a poly-language execution-based violation-witness validator
 https://github.com/polywit/polywit.

 This module deals with the building of the test harness for Kotlin programs
"""

import os
from typing import Tuple, List

from polywit.base import TestHarness, PolywitTestResult
from polywit.types import Assumption


class KotlinTestHarness(TestHarness):
    """
    The class KotlinTestHarness manages all the tests creation and compilation
    of the test harness
    """

    def __init__(self, directory):
        """
        The constructor of KotlinTestHarness collects information on the output directory

        :param directory: Directory that the harness will write to
        """
        super().__init__(directory)

    @property
    def verifier_path(self):
        return ''

    @property
    def test_path(self):
        return ''

    @property
    def compile_cmd(self):
        return ['kotlinc']

    @property
    def run_cmd(self):
        return ['java', '-jar', 'Test.jar']

    def build_test_harness(self, assumptions: List[Assumption]) -> None:
        """
        Constructs and compiles the test harness consisting of
        the unit tests and the test verifier

        :param assumptions: Assumptions extracted from the witness
        """
        return

    def _parse_test_result(self, test_output: str, test_error: str) -> PolywitTestResult:
        """
        Parses the test result and returns appropriate message

        :param test_output: Stdout from test run
        :param test_error: Stderr from test run
        """
        return PolywitTestResult.UNKNOWN
