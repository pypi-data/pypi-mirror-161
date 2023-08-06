from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.lookup import (
    download_lookup, get_table_value, column_name, extract_grouped_data, _get_single_table_value
)
from hestia_earth.utils.tools import list_sum, safe_parse_float

from ..log import debugValues


def _node_value(node):
    value = node.get('value')
    return list_sum(value) if isinstance(value, list) else value


def _factor_value(model: str, term_id: str, lookup_name: str, lookup_col: str):
    lookup = download_lookup(lookup_name)

    def get_value(data: dict):
        node_term_id = data.get('term', {}).get('@id')
        value = _node_value(data)
        coefficient = get_table_value(lookup, 'termid', node_term_id, column_name(lookup_col))
        coefficient = safe_parse_float(coefficient, None)
        if value is not None and coefficient is not None:
            debugValues(data, model=model, term=term_id,
                        node=node_term_id,
                        operation=data.get('operation', {}).get('@id'),
                        value=value,
                        coefficient=coefficient)
            return value * coefficient
        return None
    return get_value


def _term_factor_value(model: str, term_id: str, lookup_name: str, lookup_term_id: str, group_key: str = None):
    lookup = download_lookup(lookup_name, False)  # avoid saving in memory as there could be many different files used

    def get_value(data: dict):
        node_term_id = data.get('term', {}).get('@id')
        value = _node_value(data)
        coefficient = get_table_value(lookup, 'termid', lookup_term_id, column_name(node_term_id))
        coefficient = safe_parse_float(extract_grouped_data(coefficient, group_key)) if group_key else coefficient
        if value is not None and coefficient is not None:
            debugValues(data, model=model, term=term_id, node=node_term_id, value=value, coefficient=coefficient)
            return value * coefficient
        return None
    return get_value


def _aware_factor_value(model: str, term_id: str, lookup_name: str, aware_id: str, group_key: str = None):
    lookup = download_lookup(lookup_name, False)  # avoid saving in memory as there could be many different files used
    lookup_col = column_name('awareWaterBasinId')

    def get_value(data: dict):
        try:
            node_term_id = data.get('term', {}).get('@id')
            value = _node_value(data)
            coefficient = _get_single_table_value(lookup, lookup_col, int(aware_id), column_name(node_term_id))
            coefficient = safe_parse_float(extract_grouped_data(coefficient, group_key)) if group_key else coefficient
            if value is not None and coefficient is not None:
                debugValues(data, model=model, term=term_id, node=node_term_id, value=value, coefficient=coefficient)
                return value * coefficient
            return None
        except ValueError:  # factor does not exist
            return None
    return get_value


_ALLOW_ALL = 'all'


def _lookup_values(term: dict, column: str):
    lookup = download_lookup(f"{term.get('termType')}.csv")
    values = get_table_value(lookup, 'termid', term.get('@id'), column_name(column))
    return (values or _ALLOW_ALL).split(';')


def is_siteType_allowed(data: dict, term: dict):
    site = data if data.get('@type', data.get('type')) == 'Site' else data.get('site', {})
    site_type = site.get('siteType')
    allowed_values = _lookup_values(term, 'siteTypesAllowed')
    return True if _ALLOW_ALL in allowed_values or not site_type else site_type in allowed_values


def is_primary_product_termType_allowed(data: dict, term: dict):
    product = find_primary_product(data) or {}
    product_term_type = product.get('term', {}).get('termType')
    allowed_values = _lookup_values(term, 'productTermTypesAllowed')
    return True if _ALLOW_ALL in allowed_values or not product_term_type else product_term_type in allowed_values


def is_primary_product_id_allowed(data: dict, term: dict):
    product = find_primary_product(data) or {}
    product_term_id = product.get('term', {}).get('@id')
    allowed_values = _lookup_values(term, 'productTermIdsAllowed')
    return True if _ALLOW_ALL in allowed_values or not product_term_id else product_term_id in allowed_values
