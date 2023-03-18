import unittest
from unittest.mock import MagicMock, patch, Mock
from halo import Halo

from polywit.exceptions import FileProcessorError, WitnessProcessorError
from polywit.base.validator import Validator


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.file_processor = MagicMock()
        self.witness_processor = MagicMock()
        self.test_harness = MagicMock()
        self.config = {'show_assumptions': False}

    @patch('halo.Halo.succeed')
    def test_preprocess_succeeds_on_both_processor_successes(self, mock_succeed):
        # Given preprocesses return correctly
        self.file_processor.preprocess.return_value = None
        self.witness_processor.preprocess.return_value = None
        validator = self.construct_validator()
        # When preprocess is called
        validator.preprocess()
        # Then the spinner succeeds twice
        self.assertEqual(2, mock_succeed.call_count)

    @patch('halo.Halo.fail')
    @patch('halo.Halo.succeed')
    def test_preprocess_fails_on_file_processor_error(self, mock_succeed, mock_fail):
        self.file_processor.preprocess.side_effect = FileProcessorError()
        self.witness_processor.preprocess.return_value = None
        validator = self.construct_validator()
        self.assertRaises(FileProcessorError, validator.preprocess)
        self.assertEqual(0, mock_succeed.call_count)
        self.assertEqual(1, mock_fail.call_count)

    @patch('halo.Halo.fail')
    @patch('halo.Halo.succeed')
    def test_preprocess_fails_on_witness_processor_error(self, mock_succeed, mock_fail):
        self.file_processor.preprocess.return_value = None
        self.witness_processor.preprocess.side_effect = WitnessProcessorError()
        validator = self.construct_validator()
        self.assertRaises(WitnessProcessorError, validator.preprocess)
        self.assertEqual(1, mock_succeed.call_count)
        self.assertEqual(1, mock_fail.call_count)

    def construct_validator(self):
        return Validator(self.file_processor, self.witness_processor, self.test_harness, self.config)
if __name__ == '__main__':
    unittest.main()
