"""
 This file is part of polywit, a poly-language execution-based violation-witness validator
 https://github.com/polywit/polywit.

 This module deals with the processing of the witness, benchmark and packages for Java
"""
import glob
import re
from distutils.dir_util import copy_tree
import os
import networkx as nx
import javalang

from polywit.base import FileProcessor, WitnessProcessor


class JavaWitnessProcessor(WitnessProcessor):
    """
    A class representing the Java witness processor
    """

    def __init__(self, test_directory, witness_path):
        super().__init__(test_directory, witness_path)

    def preprocess(self) -> None:
        """
        Preprocess the witness to avoid any unformatted XML
        """
        # Check for malformed XML strings
        for _, assumption_edge in enumerate(filter(
                lambda edge: ('assumption.scope' in edge[2]),
                self.witness.edges(data=True)
        )):
            from_node = assumption_edge[0]
            to_node = assumption_edge[1]
            edge_data = assumption_edge[2]
            cleaned_assumption = re.sub(
                r'\(\"(.*)<(.*)>(.*)\"\)',
                r'("\1&lt;\2&gt;\3")',
                edge_data['assumption']
            )
            nx.set_edge_attributes(
                self.witness,
                {(from_node, to_node): {'assumption': cleaned_assumption}}
            )

    @staticmethod
    def _extract_value_from_assumption(assumption, regex):
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
        return assumption_value

    def extract_assumptions(self):
        """
        Extracts the assumptions from the witness
        """
        self.producer = self._get_value_from_witness('producer')
        assumptions = []
        # GDart uses different syntax for numeric types
        if self.producer == 'GDart':
            regex = r"= (-?\d*\.?\d+|false|true)|\w+\.equals\(\"(.*)\"\)|\w+\.parseDouble\(\"(" \
                    r".*)\"\)|\w+\.parseFloat\(\"(.*)\"\)"
        else:
            regex = r"= ((\S+)|(-?\d*\.?\d+[L]?)|(false|true|null))"
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
                if self.producer != 'GDart' and assumption_value == 'null':
                    assumption_value = None
                assumptions.append(((file_name, line_number), assumption_value))
        return assumptions


# noinspection PyUnresolvedReferences
class JavaFileProcessor(FileProcessor):
    """
    A class representing the Java files processor
    """

    def __init__(self, test_directory, benchmark_path, package_paths):
        super().__init__(test_directory)
        self.benchmark_path = benchmark_path
        self.package_paths = package_paths
        self.source_files = list(glob.glob(self.benchmark_path + "/**/*.java", recursive=True))

    def preprocess(self):
        copy_tree(self.benchmark_path, self.test_directory)
        for package in self.package_paths:
            copy_tree(package, self.test_directory)

    def _check_valid_import(self, import_line):
        check_file = import_line.strip().replace(".", "/").replace(";", "").replace("import", "").replace(' ', '')
        if not check_file.startswith('java'):
            # Check in working directory
            files_exists = [source_f.endswith("{0}.java".format(check_file)) for source_f in self.source_files]
            if sum(files_exists) > 1:
                raise ValueError(f'Multiple classes for {check_file} given.')
            if sum(files_exists) == 1:
                # Return full path of the only existing file definition
                return [self.source_files[files_exists.index(True)]]

            # Check in packages
            # Check for wildcard imports
            if check_file.endswith('/*'):
                wildcard_import = check_file.replace('/*', '')
                dir_exists = [p.endswith(wildcard_import) for p in self.package_paths]
                if sum(dir_exists) == 1:
                    package = self.package_paths[dir_exists.index(True)]
                    return list(glob.glob(package + "/**/*.java", recursive=True))

            full_paths = ["{0}.java".format(os.path.join(directory, check_file)) for directory in self.package_paths]
            files_exists = [os.path.exists(f_path) for f_path in full_paths]
            # Check there is only one definition for an import file and if so add to stack to check
            # for possible nondet calls
            if not any(files_exists):
                raise ValueError(f'No class for {check_file} given in classpath.')
            if sum(files_exists) > 1:
                raise ValueError(f'Multiple classes for {check_file} given in classpath.')
            else:
                # Return full path of the only existing file definition
                return [full_paths[files_exists.index(True)]]
        return []

    def extract_nondet_mappings(self):
        types_map = {}
        nondet_functions_map = {}
        extraction_stack = dict.fromkeys(self.source_files, 0)
        finished_set = {}

        while len(extraction_stack) > 0:
            filename, _ = extraction_stack.popitem()
            finished_set[filename] = 0
            program_name = filename[filename.rfind("/") + 1: filename.find(".java")]
            with open(filename, 'r', encoding='utf-8') as file:
                data = file.read()
            # Dont need to check the Verifier class
            # TODO: Change Tool definition to not pass it
            if program_name == 'Verifier':
                continue
            try:
                tree = javalang.parse.parse(data)
            except javalang.parser.JavaSyntaxError as err:
                raise err
            for import_node in tree.imports:
                files = self._check_valid_import(import_node.path)
                for file in files:
                    if file is not None and file not in extraction_stack and file not in finished_set:
                        extraction_stack[file] = 0
            # Look for nondet Calls
            for _, node in tree.filter(javalang.tree.MethodInvocation):
                if (node is not None
                        and node.qualifier is not None
                        and 'Verifier' in node.qualifier):
                    nondet_type = node.member.replace('nondet', '')
                    types_map[(program_name, node.position.line)] = nondet_type.lower()
            # Check if any nondet calls are from returns from methods
            for _, node in tree.filter(javalang.tree.MethodDeclaration):
                if node.body is None or len(node.body) == 0:
                    continue
                statement = node.body[0]
                if (isinstance(statement, javalang.tree.ReturnStatement)
                        and (program_name, statement.position.line) in types_map):
                    nondet_functions_map[node.name] = (program_name, statement.position.line)

            # Add any nondet returning functions to list of nondet function calls
            for _, node in tree.filter(javalang.tree.MethodInvocation):
                if node is not None and node.member in nondet_functions_map:
                    position = nondet_functions_map[node.member]
                    types_map[(program_name, node.position.line)] = types_map[position]

        return types_map
