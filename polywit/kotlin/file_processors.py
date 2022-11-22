"""
 This file is part of polywit, a poly-language execution-based violation-witness validator
 https://github.com/polywit/polywit.

 This module deals with the processing of the witness, benchmark and packages for Kotlin
"""
import glob
import re
from distutils.dir_util import copy_tree
import os
from typing import List

import networkx as nx

from polywit.base import FileProcessor, WitnessProcessor
from polywit.types.aliases import Assumption, Position


class KotlinWitnessProcessor(WitnessProcessor):
    """
    A class representing the Kotlin witness processor
    """

    def __init__(self, test_directory, witness_path):
        super().__init__(test_directory, witness_path)

    def preprocess(self) -> None:
        """
        Preprocess the witness to avoid any unformatted XML
        """
        super().preprocess()

    def extract_assumptions(self) -> List[Assumption]:
        """
        Extracts the assumptions from the witness
        """
        return []


class KotlinFileProcessor(FileProcessor):
    """
    A class representing the Kotlin files processor
    """

    def __init__(self, test_directory, benchmark_path, package_paths):
        super().__init__(test_directory)
        self.benchmark_path = benchmark_path
        self.package_paths = package_paths
        self.source_files = list(glob.glob(self.benchmark_path + "/**/*.kt", recursive=True))

    def preprocess(self) -> None:
        copy_tree(self.benchmark_path, self.test_directory)
        for package in self.package_paths:
            copy_tree(package, self.test_directory)

    def extract_position_type_map(self) -> dict[Position, str]:
        position_type_map: dict[Position, str] = {}
        return position_type_map
