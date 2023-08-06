from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.tools import safe_parse_float

from .term import get_lookup_value

FAO_LOOKUP_COLUMN = 'cropGroupingFAO'
FAOSTAT_AREA_LOOKUP_COLUMN = 'cropGroupingFaostatArea'
FAOSTAT_PRODUCTION_LOOKUP_COLUMN = 'cropGroupingFaostatProduction'


def get_crop_lookup_value(model: str, term_id: str, column: str):
    return get_lookup_value({'@id': term_id, 'termType': TermTermType.CROP.value}, column, model=model, term=term_id)


def get_crop_grouping_fao(model: str, term: dict):
    return get_crop_lookup_value(model, term.get('@id'), FAO_LOOKUP_COLUMN)


def get_crop_grouping_faostat_area(model: str, term: dict):
    return get_crop_lookup_value(model, term.get('@id'), FAOSTAT_AREA_LOOKUP_COLUMN)


def get_crop_grouping_faostat_production(model: str, term: dict):
    return get_crop_lookup_value(model, term.get('@id'), FAOSTAT_PRODUCTION_LOOKUP_COLUMN)


def get_N2ON_fertilizer_coeff_from_primary_product(model: str, cycle: dict):
    product = find_primary_product(cycle)
    term_id = product.get('term', {}).get('@id') if product else None
    percent = get_crop_lookup_value(model, term_id, 'N2ON_FERT') if term_id else None
    return safe_parse_float(percent, 0.01)


def is_orchard(model: str, term_id: str): return get_crop_lookup_value(model, term_id, 'isOrchard')
