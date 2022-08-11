"""
 This file is part of polywit, a poly-language execution-based violation-witness validator
 https://github.com/polywit/polywit.

 This module deals with the main functionality of the tool
"""
import os
import sys
import tempfile

from shutil import rmtree

import argparse

from polywit.validation_harnesses.java import JavaValidationHarness
from polywit.file_processors.java import JavaFileProcessor, JavaWitnessProcessor

from polywit.file_processors.utils import filter_assumptions
from polywit import __version__


def dir_path(path):
    """
    Checks if a path is a valid directory
    :param path: Potential directory
    :return: The original path if valid
    """
    if os.path.isdir(path):
        return path
    raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Creates a parser for the command-line options.
    @return: An argparse.ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="""
                   Validate a given Java program with a witness conforming to the appropriate SV-COMP
                   exchange format.
               """,
    )

    parser.add_argument(
        'benchmark',
        type=dir_path,
        help="Path to the benchmark directory"
    )

    parser.add_argument(
        '--packages',
        dest='package_paths',
        type=dir_path,
        nargs='*',
        help="Path to the packages used by the benchmark"
    )

    parser.add_argument(
        '--witness',
        dest='witness_file',
        required=True,
        type=str,
        action="store",
        help='Path to the witness file. Must conform to the exchange format'
    )

    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )

    return parser


def main():
    parser = create_argument_parser()
    config = parser.parse_args(sys.argv[1:])
    config = vars(config)
    try:
        print(f'polywit v{__version__}')

        # Create temporary directory for easier cleanup
        tmp_dir = tempfile.mkdtemp()

        # Instantiate file processors
        file_processor = JavaFileProcessor(tmp_dir, config['benchmark'], config['package_paths'])
        witness_processor = JavaWitnessProcessor(tmp_dir, config['witness_file'])

        # Need to preprocess and move to current directory to utilise mockito
        file_processor.preprocess()
        witness_processor.preprocess()

        # Process files to get type mapping and assumption list
        assumptions = witness_processor.extract_assumptions()
        nondet_mappings = file_processor.extract_nondet_mappings()
        assumption_values = filter_assumptions(nondet_mappings, assumptions)
        # Construct tests harness
        validation_harness = JavaValidationHarness(tmp_dir)
        validation_harness.build_validation_harness(assumption_values)
        outcome = validation_harness.run_validation_harness()
        print(outcome)
        # Teardown moved files
        rmtree(tmp_dir)

    except BaseException as err:
        print(f'polywit: Could not validate witness \n{err}')
    sys.exit()


if __name__ == "__main__":
    main()
