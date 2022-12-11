"""
 This file is part of polywit, a poly-language execution-based violation-witness validator
 https://github.com/polywit/polywit.

 This module deals with the processing of the witness, benchmark and packages for Kotlin
"""
import glob
import os
import re
from distutils.dir_util import copy_tree
from typing import List

from kopyt import node as kotlin_node, Parser

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

    @staticmethod
    def _extract_value_from_assumption(assumption: Assumption, regex: str) -> str:
        """
        Extracts an assumption value using a regex

        :param assumption: The string containing the variable assignment to have value extracted
        :param regex: The regular expression used to extract the value
        :return: The extracted assumption value or None if not there
        """
        search_result = re.search(regex, assumption)
        if search_result is not None:
            matches = [sr for sr in search_result.groups() if sr is not None]
            # Match the last capture group if multiple matches
            assumption_value = matches[-1]
        else:
            # Check to see if it is because nondet comes from a function return
            # and in which case it is not assigned to a variable so remove = match from regex
            regex = regex[2:]
            search_result = re.search(regex, assumption)
            if search_result is not None:
                matches = [sr for sr in search_result.groups() if sr is not None]
                # Match the last capture group if multiple matches
                assumption_value = matches[-1]
            else:
                assumption_value = None
        # Strip trailing semicolon if has been missed by regex
        if assumption_value.endswith(';'):
            assumption_value = assumption_value[:-1]
        # TODO Extract into new parser class and have methods handling specific edge values
        if assumption_value == 'Double.NaN':
            assumption_value = 'NaN'
        return str(assumption_value)

    def extract_assumptions(self) -> List[Assumption]:
        """
        Extracts the assumptions from the witness
        """
        self.producer = self._get_value_from_witness('producer')
        assumptions = []
        regex = r"= ((-?\d*\.?\d+[L]?)|(\S+)|(false|true|null))"
        for assumption_edge in filter(
                lambda edge: ('assumption.scope' in edge[2]),
                self.witness.edges(data=True)
        ):
            data = assumption_edge[2]
            file_name = self._get_file_name_from_path(data['originFileName'])
            line_number = data['startline']
            scope = data['assumption.scope']
            if file_name not in scope:
                continue
            assumption_value = self._extract_value_from_assumption(data['assumption'], regex)
            if assumption_value is not None:
                assumptions.append(((file_name, line_number), assumption_value))
        return assumptions


class KotlinFileProcessor(FileProcessor):
    """
    A class representing the Kotlin files processor
    """

    def __init__(self, test_directory, benchmark_path, package_paths):
        super().__init__(test_directory)
        self.benchmark_path = benchmark_path
        self.package_paths = package_paths if package_paths is not None else []
        self.source_files = list(glob.glob(self.benchmark_path + "/**/*.kt", recursive=True))

    def preprocess(self) -> None:
        copy_tree(self.benchmark_path, self.test_directory)
        for package in self.package_paths:
            copy_tree(package, self.test_directory)

        with open(f'{self.test_directory}/Main.kt', 'r', encoding='utf-8') as file:
            data = file.read()

        parser = Parser(data)
        result = parser.parse()

        # Rename main function
        for _, node in _filter_results(result, kotlin_node.FunctionDeclaration):
            if (node is not None
                    and node.name == 'main'):
                node.name = 'polywit_main'

        with open(f'{self.test_directory}/Main.kt', 'w', encoding='utf-8') as file:
            file.write(str(result))

    def extract_position_type_map(self) -> dict[Position, str]:
        """
        Extracts the position type map for the input files
        :return: Position type map
        """
        position_type_map: dict[Position, str] = {}
        for file_name in self.source_files:
            program_name, _ = os.path.splitext(os.path.basename(file_name))
            with open(file_name, 'r', encoding='utf-8') as file:
                data = file.read()

            parser = Parser(data)
            result = parser.parse()

            position_type_map: dict[Position, str] = {}
            for _, node in _filter_results(result, kotlin_node.PropertyDeclaration):
                if (node is not None
                        and node.value is not None
                        and hasattr(node.value, 'expression')
                        and node.value.expression.value == 'Verifier'):
                    nondet_type = node.value.suffixes[0].suffix.replace('nondet', '')
                    position_type_map[(program_name, node.position.line)] = nondet_type.lower()

        return position_type_map


def _filter_results(result, pattern):
    for path, node in _walk_tree(result.declarations):
        if (isinstance(pattern, type) and isinstance(node, pattern)) or (node == pattern):
            yield path, node


def _walk_tree(root):
    children = []
    if isinstance(root, kotlin_node.FunctionDeclaration):
        yield (), root
        if root.body is None or root.body.sequence is None:
            children = []
        else:
            children = root.body.sequence
    elif isinstance(root, kotlin_node.ClassDeclaration):
        yield (), root
        if root.body is None or root.body.members is None:
            children = []
        else:
            children = root.body.members
    elif isinstance(root, kotlin_node.Statement):
        statement = root.statement
        yield (), statement
        children = []
        if isinstance(statement, kotlin_node.TryExpression):
            children += [] if not statement.try_block.sequence else statement.try_block.sequence
            children += [] if not statement.catch_blocks else statement.catch_blocks
            children += [] if not statement.finally_block else statement.finally_block
    elif isinstance(root, kotlin_node.CatchBlock):
        yield (), root
        children = root.block.sequence
    elif isinstance(root, kotlin_node.PropertyDeclaration):
        yield (), root
        children = []
    else:
        children = root

    for child in children:
        if isinstance(child, kotlin_node.Node):
            for path, node in _walk_tree(child):
                yield (root,) + path, node
