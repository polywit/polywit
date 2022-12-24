import tempfile
from unittest import TestCase

from polywit.base import WitnessProcessor


class TestWitnessProcessor(TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.witness_processor = WitnessProcessor(self.tmp_dir)

    def test_get_file_name_from_path(self):
        path = 'home/benchmarks/SomeFileName.java'
        file_name = self.witness_processor._get_file_name_from_path(path)
        self.assertEqual('SomeFileName1', file_name)
