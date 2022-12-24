import tempfile
from unittest import TestCase

from polywit.base import WitnessProcessor


class TestWitnessProcessor(TestCase):

    def test_get_file_name_from_valid_path(self):
        path = 'home/benchmarks/SomeFileName.java'
        file_name = WitnessProcessor._get_file_name_from_path(path)
        self.assertEqual('SomeFileName', file_name)

    def test_get_file_name_from_valid_path_without_extension(self):
        path = 'home/benchmarks/SomeFileName'
        file_name = WitnessProcessor._get_file_name_from_path(path)
        self.assertEqual('SomeFileName', file_name)
