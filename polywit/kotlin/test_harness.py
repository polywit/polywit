"""
 This file is part of polywit, a poly-language execution-based violation-witness validator
 https://github.com/polywit/polywit.

 This module deals with the building of the test harness for Kotlin programs
"""

import os
from typing import Tuple, List

from polywit.exceptions import TestHarnessExecutionError, validation_error_handler, TestHarnessConstructionError
from polywit.base import TestHarness, PolywitTestResult
from polywit._typing import Assumption


class KotlinTestHarness(TestHarness):
    """
    The class KotlinTestHarness manages all the tests creation and compilation
    of the test harness
    """
    VERIFIER_PACKAGE = 'org/polywit/benchmarks'

    VERIFIER_RESOURCE_PATH = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'resources/Verifier.kt'
    )
    TEST_RESOURCE_PATH = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'resources/Test.kt'
    )

    def __init__(self, directory):
        """
        The constructor of KotlinTestHarness collects information on the output directory

        :param directory: Directory that the harness will write to
        """
        super().__init__(directory)

    @property
    def verifier_path(self):
        return os.path.join(
            self.directory,
            f'{self.VERIFIER_PACKAGE}/Verifier.kt'
        )

    @property
    def test_path(self):
        return os.path.join(
            self.directory,
            'Test.kt'
        )

    @property
    def main_path(self):
        return os.path.join(
            self.directory,
            'Main.kt'
        )

    @property
    def jar_path(self):
        return os.path.join(
            self.directory,
            'Test.jar'
        )

    @property
    def compile_cmd(self):
        return ['kotlinc', self.test_path, self.main_path, self.verifier_path, '-include-runtime', '-d', self.jar_path]

    @property
    def run_cmd(self):
        return ['java', '-ea', '-jar', self.jar_path]

    @validation_error_handler(TestHarnessConstructionError)
    def build_test_harness(self, assumptions: List[Assumption]) -> None:
        """
        Constructs and compiles the test harness consisting of
        the unit tests and the test verifier

        :param assumptions: Assumptions extracted from the witness
        """
        self._build_unit_test()
        self._build_test_verifier(assumptions)
        _, _ = self._compile_test_harness()

    def _build_unit_test(self) -> None:
        """
        Constructs the unit tests from Test.kt
        """
        test_data = self._read_data(self.TEST_RESOURCE_PATH)
        self._write_data(self.test_path, test_data)

    def _build_test_verifier(self, assumptions: List[Assumption]) -> None:
        """
        Constructs the tests verifier from a list of assumptions
        and Verifier.java

        :param assumptions: Assumptions extracted from the witness
        """
        verifier_path = os.path.join(
            self.directory,
            f'{self.VERIFIER_PACKAGE}/Verifier.kt'
        )
        # We only need assumption values so extract them
        assumption_values = list(map(lambda assumption: assumption[1], assumptions))
        # Map assumptions to string form, mapping None to null
        string_assumptions = [f'"{a}"' if a is not None else 'null' for a in assumption_values]
        verifier_data = self._read_data(self.VERIFIER_RESOURCE_PATH)
        # Replace empty assumptions list with extracted assumptions if they exist
        if len(string_assumptions) > 0:
            assumption_line = verifier_data.index('    var assumptionList = emptyArray<String>()\n')
            verifier_data[assumption_line] = verifier_data[assumption_line].replace(
                'emptyArray<String>()',
                'arrayOf(' + ', '.join(string_assumptions) + ')'
            )
        self._write_data(verifier_path, verifier_data)

    def _compile_test_harness(self) -> Tuple[str, str]:
        """
        Compiles the tests harness

        :return: stdout and stderr from compilation
        """
        out, err = self._run_command(self.compile_cmd)
        return out, err

    @validation_error_handler(TestHarnessExecutionError)
    def run_test_harness(self) -> PolywitTestResult:
        """
        Runs the test harness and reports the outcome of the test execution

        :return: The test result
        """
        out, err = self._run_command(self.run_cmd)
        return self._parse_test_result(
            out,
            err,
            'java.lang.AssertionError',
            'polywit: Witness Spurious'
        )
