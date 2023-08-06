from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, extract_grouped_data
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugMissingLookup, logRequirements
from hestia_earth.models.utils.impact_assessment import get_site, get_country_id
from . import MODEL


def _lookup_value(term_id: str, lookup_name: str, col_match: str, col_val: str, column: str, group_key: str = None):
    value = get_table_value(download_lookup(f"{lookup_name}.csv"), col_match, col_val, column_name(column))
    value = extract_grouped_data(value, group_key) if group_key else value
    debugMissingLookup(f"{lookup_name}.csv", col_match, col_val, column, value, model=MODEL, term=term_id)
    return safe_parse_float(value)


def get_region_factor(term_id: str, impact_assessment: dict, lookup_suffix: str, group_key: str = None):
    site = get_site(impact_assessment)
    ecoregion = site.get('ecoregion')
    country_id = get_country_id(impact_assessment)
    site_type = site.get('siteType')

    lookup_prefix = 'ecoregion' if ecoregion else 'region' if country_id else None
    col_name = 'ecoregion' if ecoregion else 'termid'
    col_val = ecoregion or country_id

    logRequirements(impact_assessment, model=MODEL, term=term_id,
                    site_type=site_type,
                    ecoregion=ecoregion,
                    country_id=country_id)

    return _lookup_value(term_id, f"{lookup_prefix}-siteType-{lookup_suffix}", col_name, col_val, site_type, group_key)
