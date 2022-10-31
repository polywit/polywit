from typing import List

from polywit.types import Assumption, Position


def filter_assumptions(position_type_map: dict[Position, str], assumptions: List[Assumption]) -> List[Assumption]:
    """
    Filters assumptions to only contain assumptions coming from nondet function calls.
    :param position_type_map: A mapping from a position of a nondet call to its type
    :param assumptions: A list of assumptions
    :return: A list of assumptions values that come from nondet functions
    """
    return list(filter(lambda assumption: (assumption[0] in position_type_map), assumptions))
