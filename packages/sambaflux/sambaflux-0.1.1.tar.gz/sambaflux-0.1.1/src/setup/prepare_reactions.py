"""
Functions for preparing reactions in a metabolic model.
"""


def set_exchanges_rxn_bounds(model, exchange_min):
    """

    :param model:
    :param exchange_min:
    :return: model:
    """
    # Set the exchange reaction bounds
    for rxn in model.exchanges:
        rxn.lower_bound = -exchange_min
        rxn.upper_bound = 1000
    return model


def parse_rxns(filename, sep=" "):
    if filename is None:
        return None
    with open(filename, 'r') as file:
        ids = [i.strip().split(sep) for i in file]
    return ids

