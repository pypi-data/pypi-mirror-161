from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.tools import list_sum, safe_parse_float

from ..log import debugValues
from . import emission, _filter_list_term_unit
from .constant import Units
from .property import get_node_property
from .lookup import is_siteType_allowed, is_primary_product_id_allowed, is_primary_product_termType_allowed


def _run_required(model: str, term_id: str, data: dict):
    term = download_hestia(term_id)
    # skip completely if the model is not a Term
    if not term:
        return True
    siteType_allowed = is_siteType_allowed(data, term)
    primary_product_id_allowed = is_primary_product_id_allowed(data, term)
    primary_product_termType_allowed = is_primary_product_termType_allowed(data, term)

    run_required = all([siteType_allowed, primary_product_id_allowed, primary_product_termType_allowed])
    debugValues(data, model=model, term=term_id,
                run_required=run_required,
                siteType_allowed=siteType_allowed,
                primary_product_id_allowed=primary_product_id_allowed,
                primary_product_termType_allowed=primary_product_termType_allowed)
    return run_required


def _run_required_default(model: str, term_id: str, data: dict, module):
    return getattr(module, 'run')(data)


def _run_required_measurement(model: str, term_id: str, data: dict, module):
    return getattr(module, 'run')(data) if _run_required(model, term_id, data) else []


def _run_required_practice(model: str, term_id: str, data: dict, module):
    return getattr(module, 'run')(data) if _run_required(model, term_id, data) else []


def _run_required_emission(model: str, term_id: str, data: dict, module):
    return getattr(module, 'run')(data) if _run_required(model, term_id, data) \
        else emission._default_emission(model, term_id, data, getattr(module, 'RETURNS', {}))


RUN_REQUIRED_BY_TYPE = {
    'Measurement': _run_required_measurement,
    'Practice': _run_required_practice,
    'Emission': _run_required_emission
}


def run_if_required(model: str, term_id: str, data: dict, module):
    return_type = list(getattr(module, 'RETURNS', {'': None}).keys())[0]
    return RUN_REQUIRED_BY_TYPE.get(return_type, _run_required_default)(model, term_id, data, module)


def find_terms_value(nodes: list, term_id: str):
    """
    Returns the sum of all blank nodes in the list which match the `Term` with the given `@id`.

    Parameters
    ----------
    values : list
        The list in which to search for. Example: `cycle['nodes']`.
    term_id : str
        The `@id` of the `Term`. Example: `sandContent`

    Returns
    -------
    float
        The total `value` as a number.
    """
    return list_sum(get_total_value(filter(lambda node: node.get('term', {}).get('@id') == term_id, nodes)))


def get_total_value(nodes: list):
    """
    Get the total `value` of a list of Blank Nodes.
    This method does not take into account the `units` and possible conversions.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The total `value` as a list of numbers.
    """
    return list(map(lambda node: list_sum(node.get('value', [])), nodes))


def _value_as(term_id: str, convert_to_property=True):
    def get_value(node: dict):
        property = get_node_property(node, term_id)
        # ignore node value if property is not found
        factor = safe_parse_float(property.get('value', 0))
        value = list_sum(node.get('value', []))
        ratio = factor / 100 if property.get('term', {}).get('units', '') == '%' else factor
        return 0 if ratio == 0 else (value * ratio if convert_to_property else value / ratio)
    return get_value


def get_total_value_converted(nodes: list, conversion_property, convert_to_property=True):
    """
    Get the total `value` of a list of Blank Nodes converted using a property of each Blank Node.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.
    conversion_property : str|List[str]
        Property (or multiple properties) used for the conversion. Example: `nitrogenContent`.
        See https://hestia.earth/glossary?termType=property for a list of `Property`.
    convert_to_property : bool
        By default, property is multiplied on value to get result. Set `False` to divide instead.

    Returns
    -------
    list
        The total `value` as a list of numbers.
    """
    def convert_multiple(node: dict):
        value = 0
        for prop in conversion_property:
            value = _value_as(prop, convert_to_property)(node)
            node['value'] = [value]
        return value

    return [
        _value_as(conversion_property, convert_to_property)(node) if isinstance(conversion_property, str) else
        convert_multiple(node) for node in nodes
    ]


def get_N_total(nodes: list) -> list:
    """
    Get the total nitrogen content of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every blank node in `kg N` will be used.
    2. Every blank node specified in `kg` will be multiplied by the `nitrogenContent` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The nitrogen values as a list of numbers.
    """
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, Units.KG)
    return get_total_value(kg_N_nodes) + get_total_value_converted(kg_nodes, 'nitrogenContent')


def get_KG_total(nodes: list) -> list:
    """
    Get the total kg mass of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every blank node in `kg` will be used.
    2. Every blank node specified in `kg N` will be divided by the `nitrogenContent` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The nitrogen values as a list of numbers.
    """
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, Units.KG)
    return get_total_value(kg_nodes) + get_total_value_converted(kg_N_nodes, 'nitrogenContent', False)


def get_P2O5_total(nodes: list) -> list:
    """
    Get the total phosphate content of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every organic fertilizer specified in `kg P2O5` will be used.
    1. Every organic fertilizer specified in `kg N` will be multiplied by the `phosphateContentAsP2O5` property.
    2. Every organic fertilizer specified in `kg` will be multiplied by the `phosphateContentAsP2O5` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The phosphate values as a list of numbers.
    """
    kg_P_nodes = _filter_list_term_unit(nodes, Units.KG_P2O5)
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, Units.KG)
    return get_total_value(kg_P_nodes) + get_total_value_converted(kg_N_nodes + kg_nodes, 'phosphateContentAsP2O5')
