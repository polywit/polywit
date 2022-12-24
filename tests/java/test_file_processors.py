import tempfile
from unittest import TestCase

from polywit.java import JavaWitnessProcessor


class TestJavaWitnessProcessor(TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.witness_processor = JavaWitnessProcessor(self.tmp_dir, '')

    def test_preprocess(self):
        self.witness_processor.preprocess()
        self.fail()

    def test__extract_value_from_assumption(self):
        self.fail()

    def test_extract_assumptions(self):
        self.fail()
