def filter_assumptions(nondet_mappings, assumptions_list):
    """
    Filters assumptions to only contain values from nondet function calls.
    :param nondet_mappings: A mapping from a position of a nondet call to its type
    :param assumptions_list: A list of assumptions
    :return: A list of assumptions values that come from nondet functions
    """
    filtered_assumptions = filter(lambda assumption: (assumption[0] in nondet_mappings), assumptions_list)
    return list(map(lambda assumption: assumption[1], filtered_assumptions))
