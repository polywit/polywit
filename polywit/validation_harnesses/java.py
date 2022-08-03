"""
 This file is part of polywit, a poly-language execution-based violation-witness validator
 https://github.com/polywit/polywit.

 This module deals with the building of the validation harness for Java programs
"""

import os
from typing import Tuple

from polywit.validation_harnesses.base import BaseValidationHarness


class JavaValidationHarness(BaseValidationHarness):
    """
    The class JavaValidationHarness manages all the tests creation and compilation
    of the validation harness
    """
    VERIFIER_PACKAGE = 'org/sosy_lab/sv_benchmarks'
    VERIFIER_RESOURCE_PATH = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'resources/java/Verifier.java'
    )
    TEST_RESOURCE_PATH = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'resources/java/Test.java'
    )

    def __init__(self, directory):
        """
        The constructor of TestBuilder collects information on the output directory
        :param directory: Directory that the harness will write to
        """
        super().__init__(directory)
        self.verifier_path = os.path.join(
            self.directory,
            f'{self.VERIFIER_PACKAGE}/Verifier.java'
        )
        self.test_path = os.path.join(
            self.directory,
            'Test.java'
        )
        self.run_args = ['java', '-cp', self.directory, '-ea', 'Test']

    def build_validation_harness(self, assumptions) -> None:
        """
         Constructs and compiles the validator harness consisting of
         the unit tests and the test verifier
        :param assumptions: Assumptions extracted from the witness
        """
        super().build_test_harness(assumptions)
        _, _ = self._compile_test_harness()

    def _build_unit_test(self) -> None:
        """
        Constructs the unit tests from Test.java
        """
        test_data = self._read_data(self.TEST_RESOURCE_PATH)
        self._write_data(self.test_path, test_data)

    def _build_test_verifier(self, assumptions) -> None:
        """
        Constructs the tests verifier from a list of assumptions
        and Verifier.java
        :param assumptions: Assumptions extracted from the witness
        """
        verifier_path = os.path.join(
            self.directory,
            f'{self.VERIFIER_PACKAGE}/Verifier.java'
        )
        # Map assumptions to string form, mapping None to null
        string_assumptions = [f'"{a}"' if a is not None else 'null' for a in assumptions]
        verifier_data = self._read_data(self.VERIFIER_RESOURCE_PATH)
        # Replace empty assumptions list with extracted assumptions
        assumption_line = verifier_data.index('  static String[] assumptionList = {};\n')
        verifier_data[assumption_line] = verifier_data[assumption_line].replace(
            '{}',
            '{' + ', '.join(string_assumptions) + '}'
        )
        self._write_data(verifier_path, verifier_data)

    def _compile_test_harness(self) -> Tuple[str, str]:
        """
        Compiles the tests harness
        :return: stdout and stderr from compilation
        """
        compile_args = ['javac', '-sourcepath', self.directory, self.test_path]
        out, err = self._run_command(compile_args)
        return out, err

    def _parse_validation_result(self, validation_output, validation_error) -> None:
        """
        Parses the validation result and returns appropriate message
        :param validation_output: Stdout from validation run
        :param validation_error: Stderr from validation run
        """
        # Set output to be stderr if there is some erroneous output
        validation_output = validation_error if validation_error else validation_output
        if 'Exception in thread "main" java.lang.AssertionError' in validation_output:
            return 'polywit: Witness Correct'
        if 'wit4java: Witness Spurious' in validation_output:
            return 'polywit: Witness Spurious'
        return 'polywit: Could not validate witness'
