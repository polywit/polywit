import pytest

from unittest.mock import MagicMock, patch
from textwrap import indent

from polywit.base.test_harness import PolywitTestResult
from tabulate import tabulate

from polywit.exceptions import FileProcessorError, WitnessProcessorError, TestHarnessError
from polywit.base.validator import Validator

ASSUMPTION_1 = (('File1', 1), '3')
POSITION_TYPE_1 = {('File1', 1): 'int'}
ASSUMPTION_2 = (('File1', 3), 'Juice')
POSITION_TYPE_2 = {('File1', 3): 'str'}

EMPTY_ASSUMPTIONS = []

EXAMPLE_TABLE = indent(
    tabulate(
        [(f'{ASSUMPTION_1[0][0]}:{ASSUMPTION_1[0][1]}',
          ASSUMPTION_1[1], POSITION_TYPE_1[ASSUMPTION_1[0]])],
        headers=['Position', 'Value', 'Type'], tablefmt="pretty"),
    '  ')


def load_example_filtered_assumptions():
    return [
        ([ASSUMPTION_1], POSITION_TYPE_1, [ASSUMPTION_1]),
        ([ASSUMPTION_1], POSITION_TYPE_1 | POSITION_TYPE_2, [ASSUMPTION_1]),
        ([ASSUMPTION_1], POSITION_TYPE_2, EMPTY_ASSUMPTIONS),
        ([ASSUMPTION_1, ASSUMPTION_2], POSITION_TYPE_1 | POSITION_TYPE_2, [ASSUMPTION_1, ASSUMPTION_2]),
    ]


class TestValidator:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.file_processor = MagicMock()
        self.witness_processor = MagicMock()
        self.test_harness = MagicMock()
        self.config = {'show_assumptions': False}
        yield

    @patch('halo.Halo.succeed')
    def test_preprocess_succeeds_on_both_processor_successes(self, mock_succeed):
        # Given preprocesses return correctly
        self.file_processor.preprocess.return_value = None
        self.witness_processor.preprocess.return_value = None
        validator = self.construct_validator()
        # When preprocess is called
        validator.preprocess()
        # Then the spinner succeeds twice
        assert mock_succeed.call_count == 2

    @patch('halo.Halo.fail')
    @patch('halo.Halo.succeed')
    def test_preprocess_fails_on_file_processor_error(self, mock_succeed, mock_fail):
        self.file_processor.preprocess.side_effect = FileProcessorError()
        self.witness_processor.preprocess.return_value = None
        validator = self.construct_validator()
        with pytest.raises(FileProcessorError):
            validator.preprocess()
        assert mock_succeed.call_count == 0
        assert mock_fail.call_count == 1

    @patch('halo.Halo.fail')
    @patch('halo.Halo.succeed')
    def test_preprocess_fails_on_witness_processor_error(self, mock_succeed, mock_fail):
        self.file_processor.preprocess.return_value = None
        self.witness_processor.preprocess.side_effect = WitnessProcessorError()
        validator = self.construct_validator()
        with pytest.raises(WitnessProcessorError):
            validator.preprocess()
        assert mock_succeed.call_count == 1
        assert mock_fail.call_count == 1

    @pytest.mark.parametrize('non_filtered_assumptions,position_type_map,filtered_assumptions',
                             load_example_filtered_assumptions())
    def test_correct_assumptions_extracted(self,
                                           non_filtered_assumptions,
                                           position_type_map,
                                           filtered_assumptions):
        self.witness_processor.extract_assumptions.return_value = non_filtered_assumptions
        self.file_processor.extract_position_type_map.return_value = position_type_map
        validator = self.construct_validator()
        assumptions = validator.extract_assumptions()
        assert assumptions == filtered_assumptions

    @patch('builtins.print')
    def test_assumptions_can_be_outputted(self, mock_print):
        self.config['show_assumptions'] = True
        self.witness_processor.extract_assumptions.return_value = [ASSUMPTION_1]
        self.file_processor.extract_position_type_map.return_value = POSITION_TYPE_1
        validator = self.construct_validator()
        _ = validator.extract_assumptions()
        mock_print.assert_called_once_with(EXAMPLE_TABLE)

    @patch('halo.Halo.fail')
    @patch('halo.Halo.succeed')
    def test_extract_assumption_fails_on_extract_position_type_map(self, mock_succeed, mock_fail):
        self.file_processor.extract_position_type_map.side_effect = FileProcessorError()
        validator = self.construct_validator()
        with pytest.raises(FileProcessorError):
            validator.extract_assumptions()
        assert mock_succeed.call_count == 0
        assert mock_fail.call_count == 1

    @patch('halo.Halo.fail')
    @patch('halo.Halo.succeed')
    def test_extract_assumption_fails_on_extract_assumptions(self, mock_succeed, mock_fail):
        self.witness_processor.extract_assumptions.side_effect = WitnessProcessorError()
        self.file_processor.extract_position_type_map.side_effect = POSITION_TYPE_1
        validator = self.construct_validator()
        with pytest.raises(WitnessProcessorError):
            validator.extract_assumptions()
        assert mock_succeed.call_count == 1
        assert mock_fail.call_count == 1

    @patch('halo.Halo.succeed')
    def test_execute_test_harness_successfully(self, mock_succeed):
        self.test_harness.build_test_harness.return_value = None
        self.test_harness.run_test_harness.return_value = PolywitTestResult.CORRECT
        validator = self.construct_validator()
        result = validator.execute_test_harness(EMPTY_ASSUMPTIONS)
        assert mock_succeed.call_count == 2
        assert result == PolywitTestResult.CORRECT

    @patch('halo.Halo.fail')
    @patch('halo.Halo.succeed')
    def test_execute_test_harness_fails_when_cannot_build_harness(self, mock_succeed, mock_fail):
        self.test_harness.build_test_harness.side_effect = TestHarnessError()
        validator = self.construct_validator()
        with pytest.raises(TestHarnessError):
            validator.execute_test_harness(EMPTY_ASSUMPTIONS)
        assert mock_succeed.call_count == 0
        assert mock_fail.call_count == 1

    @patch('halo.Halo.fail')
    @patch('halo.Halo.succeed')
    def test_execute_test_harness_fails_when_cannot_run_harness(self, mock_succeed, mock_fail):
        self.test_harness.build_test_harness.return_value = None
        self.test_harness.run_test_harness.side_effect = TestHarnessError()
        validator = self.construct_validator()
        with pytest.raises(TestHarnessError):
            validator.execute_test_harness(EMPTY_ASSUMPTIONS)
        assert mock_succeed.call_count == 1
        assert mock_fail.call_count == 1

    def construct_validator(self):
        return Validator(self.file_processor, self.witness_processor, self.test_harness, self.config)
