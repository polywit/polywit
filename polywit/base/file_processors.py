"""
 This file is part of polywit, a poly-language execution-based violation-witness validator
 https://github.com/polywit/polywit.

 This module deals with the base definitions for processing of the witness and compilation units
"""

from abc import ABC, abstractmethod
import os
from typing import List, Optional

import networkx as nx

from polywit._typing import Position, Assumption


class Processor(ABC):
    """
    An abstract class representing the base functionality for a processor
    """

    def __init__(self, test_directory):
        self.test_directory = test_directory

    @abstractmethod
    def preprocess(self) -> None:
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

    @abstractmethod
    def extract_position_type_map(self) -> dict[Position, str]:
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
        self.witness = None

    def preprocess(self) -> None:
        if self.witness is None:
            try:
                self.witness = nx.read_graphml(self.witness_path)
            except Exception as exc:
                raise ValueError(f'Witness file is not formatted correctly. \n {exc}') from exc
        # Check witness is linear
        self._check_witness_linearity()

    def _check_witness_linearity(self) -> None:
        """
        Checks the witness is a linear violation witness before building validator
        """
        entry_nodes = list(filter(
            lambda nodes: nodes[1],
            self.witness.nodes.data('isEntryNode', default=False)
        ))
        if len(entry_nodes) != 1:
            raise ValueError('Witness does not have a single entry node')
        self.entry_node = entry_nodes[0][0]
        violation_nodes = list(filter(
            lambda nodes: nodes[1],
            self.witness.nodes.data('isViolationNode', default=False)
        ))
        if len(violation_nodes) == 0:
            raise ValueError('No support for non violation-witnesses')
        elif len(violation_nodes) > 1:
            raise ValueError('Witness does not have a single violation node')
        self.violation_node = violation_nodes[0][0]
        if len(list(nx.all_simple_paths(self.witness, source=self.entry_node, target=self.violation_node))) > 1:
            raise ValueError('Witness has multiple execution paths from source to sink')

    def _get_value_from_witness(self, key) -> Optional[str]:
        return self.witness.graph[key] if key in self.witness.graph else None

    @abstractmethod
    def extract_assumptions(self) -> List[Assumption]:
        """
        Extracts the assumptions from the witness
        """

    @staticmethod
    def _get_file_name_from_path(path):
        """
        Returns the file name
        :param path: Path to file
        :return: Base file name without the extension
        """
        base_name = os.path.basename(path)
        return os.path.splitext(base_name)[0]
