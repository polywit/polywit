"""
 This file is part of wit4java, an execution-based violation-witness validator for Java
 https://github.com/wit4java/wit4java.

 This module deals with the processing of the witness, benchmark and packages
"""
import glob
from abc import ABC, abstractmethod
import re
from distutils.dir_util import copy_tree
import os
class Processor(ABC):
    """
    An abstract class representing the base functionality for a processor
    """

    def __init__(self, test_directory):
        self.test_directory = test_directory

    @abstractmethod
    def preprocess(self):
        """
        Stub for the preprocess method
        """

    def write_to_test_directory(self, path, data):
        """
        Writes some data to the working directory at some given path offset
        :param path: The offset path from the working directory
        :param data: The data to be written
        :return: The new place the data was written to.
        """
        # Check if incoming path involves a new subdirectory
        subdir = os.path.join(self.test_directory, os.path.dirname(path))
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        new_path = os.path.join(self.test_directory, path)
        with open(new_path, 'w', encoding='utf-8') as file:
            file.write(data)

        return new_path

class FileProcessor(Processor):
    """
    An abstract class representing the base functionality for a file processor
    """

    def __init__(self, test_directory):
        super().__init__(test_directory)

    def extract_nondet_mappings(self):
        """
        Stub for the extract nondet mappings method
        """

class FileProcessor(ABC):
    """
    An abstract class representing the base functionality for a file processor
    """

    def __init__(self, test_directory):
        self.test_directory = test_directory

    @abstractmethod
    def extract_nondet_mappings(self):
        """
        Stub for the extract nondet mappings method
        """


class WitnessProcessor(Processor):
    """
    A class representing the witness processor
    """

    def __init__(self, test_directory, witness_path):
        super().__init__(test_directory)
        self.producer = None
        self.witness_path = witness_path

    @abstractmethod
    def extract_assumptions(self):
        """
        Extracts the assumptions from the witness
        """
