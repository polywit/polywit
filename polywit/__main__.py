"""
 This file is part of polywit, a poly-language execution-based violation-witness validator
 https://github.com/polywit/polywit.

 This module deals with the main functionality of the tool
"""

import os
import sys

import argparse

from polywit import __version__
from polywit.java import JavaValidator
from polywit.kotlin import KotlinValidator


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
                   Validate a given program with a witness conforming to the appropriate SV-COMP
                   exchange format.
               """,
    )

    parser.add_argument(
        "--version", action="version", version=f'polywit: v{__version__}'
    )
    subparsers = parser.add_subparsers(
        metavar='frontend',
        dest='language',
        help='Frontend language'
    )

    base_subparser = argparse.ArgumentParser(add_help=False)

    # define common shared arguments
    base_subparser.add_argument(
        '--show-assumptions',
        action='store_true',
        help="Shows the extracted assumptions from the witness"
    )

    java_sub_parser = subparsers.add_parser(
        'java',
        help='Use the java validator',
        parents=[base_subparser]
    )

    java_sub_parser.add_argument(
        'benchmark',
        type=dir_path,
        help="Path to the benchmark directory"
    )

    java_sub_parser.add_argument(
        '--packages',
        dest='package_paths',
        type=dir_path,
        nargs='*',
        help="Path to the packages used by the benchmark"
    )

    java_sub_parser.add_argument(
        '--witness',
        dest='witness_file',
        required=True,
        type=str,
        action="store",
        help='Path to the witness file. Must conform to the exchange format'
    )

    kotlin_sub_parser = subparsers.add_parser(
        'kotlin',
        help='Use the kotlin validator',
        parents=[base_subparser]
    )

    kotlin_sub_parser.add_argument(
        'benchmark',
        type=dir_path,
        help="Path to the benchmark directory"
    )

    kotlin_sub_parser.add_argument(
        '--packages',
        dest='package_paths',
        type=dir_path,
        nargs='*',
        help="Path to the packages used by the benchmark"
    )

    kotlin_sub_parser.add_argument(
        '--witness',
        dest='witness_file',
        required=True,
        type=str,
        action="store",
        help='Path to the witness file. Must conform to the exchange format'
    )

    return parser


def main():
    parser = create_argument_parser()
    config = parser.parse_args(sys.argv[1:])
    config = vars(config)
    try:
        print(f'polywit: v{__version__}')
        match config['language']:
            case 'java':
                validator = JavaValidator(config)
            case 'kotlin':
                validator = KotlinValidator(config)
            case _:
                raise ValueError("Validator not yet supported")
        validator.preprocess()
        assumptions = validator.extract_assumptions()
        outcome = validator.execute_test_harness(assumptions)
        print(f'{outcome}')

    except BaseException as err:
        validator.spinner.fail()
        print(f'polywit: Could not validate witness \n{err}')
    sys.exit()


if __name__ == "__main__":
    main()
