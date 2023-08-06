from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import list_sum, safe_parse_date

from .lookup import _factor_value, _term_factor_value, _aware_factor_value


def impact_end_year(impact_assessment: dict) -> int:
    """
    End year of the `ImpactAssessment`.

    Parameters
    ----------
    impact_assessment : dict
        The `ImpactAssessment`.

    Returns
    -------
    number
        The year in which the `ImpactAssessment` ends.
    """
    date = safe_parse_date(impact_assessment.get('endDate'))
    return date.year if date else None


def get_product(impact_assessment: dict) -> dict:
    """
    Get the full `Product` from the `ImpactAssessment.cycle`.

    Parameters
    ----------
    impact_assessment : dict
        The `ImpactAssessment`.

    Returns
    -------
    dict
        The `Product` of the `ImpactAssessment`.
    """
    product = impact_assessment.get('product', {})
    products = impact_assessment.get('cycle', {}).get('products', [])
    return find_term_match(products, product.get('@id'))


def get_site(impact_assessment: dict) -> dict:
    return impact_assessment.get('site', impact_assessment.get('cycle', {}).get('site', {}))


def get_region_id(impact_assessment: dict) -> str:
    """
    Get the country or region @id of the ImpactAssessment.
    Note: level 1 GADM region will be returned only, even if the region is of level > 1.

    Parameters
    ----------
    impact_assessment : dict
        The `ImpactAssessment`.

    Returns
    -------
    str
        The `@id` of the `region`.
    """
    site = get_site(impact_assessment)
    term_id = site.get('region', site.get('country', impact_assessment.get('country', {}))).get('@id')
    is_allowed = term_id is None or len(term_id) == 8 or not term_id.startswith('GADM')
    term_parts = term_id.split('.') if term_id else []
    return term_id if is_allowed else (
        f"{'.'.join(term_parts[0:2])}{('_' + term_id.split('_')[1]) if len(term_parts) > 2 else ''}"
    )


def get_country_id(impact_assessment: dict) -> str:
    """
    Get the country or @id of the ImpactAssessment.

    Parameters
    ----------
    impact_assessment : dict
        The `ImpactAssessment`.

    Returns
    -------
    str
        The `@id` of the `country`.
    """
    return impact_assessment.get('country', get_site(impact_assessment).get('country', {})).get('@id')


def impact_lookup_value(model: str, term_id: str, impact: dict, lookup_col: str) -> float:
    """
    Calculate the value of the impact based on lookup factors and emissions value.

    Parameters
    ----------
    model : str
        The model to display in the logs only.
    term_id : str
        The term to display in the logs only.
    impact_assessment : dict
        The `ImpactAssessment`.
    lookup_col : str
        The lookup column to fetch the factors from.

    Returns
    -------
    int
        The impact total value.
    """
    nodes = impact.get('emissionsResourceUse', [])
    factors = list(map(_factor_value(model, term_id, 'emission.csv', lookup_col), nodes))
    values = [value for value in factors if value is not None]
    return list_sum(values) if len(values) > 0 else None


def impact_country_value(model: str, term_id: str, impact: dict, lookup: str, group_key: str = None) -> float:
    """
    Calculate the value of the impact based on lookup factors and `site.country.@id`.

    Parameters
    ----------
    model : str
        The model to display in the logs only.
    term_id : str
        The term to display in the logs only.
    impact_assessment : dict
        The `ImpactAssessment`.
    lookup : str
        The name of the lookup to fetch the factors from.
    group_key : str
        Optional: key to use if the data is a group of values.

    Returns
    -------
    int
        The impact total value.
    """
    nodes = impact.get('emissionsResourceUse', [])
    country_id = get_country_id(impact)
    factors = list(map(_term_factor_value(model, term_id, lookup, country_id, group_key), nodes))
    values = [value for value in factors if value is not None]
    return list_sum(values) if len(values) > 0 else None


def impact_aware_value(model: str, term_id: str, impact: dict, lookup: str, group_key: str = None) -> float:
    """
    Calculate the value of the impact based on lookup factors and `site.awareWaterBasinId`.

    Parameters
    ----------
    model : str
        The model to display in the logs only.
    term_id : str
        The term to display in the logs only.
    impact_assessment : dict
        The `ImpactAssessment`.
    lookup : str
        The name of the lookup to fetch the factors from.
    group_key : str
        Optional: key to use if the data is a group of values.

    Returns
    -------
    int
        The impact total value.
    """
    nodes = impact.get('emissionsResourceUse', [])
    site = get_site(impact)
    aware_id = site.get('awareWaterBasinId')
    if aware_id is None:
        return None
    factors = list(map(_aware_factor_value(model, term_id, lookup, aware_id, group_key), nodes))
    values = [value for value in factors if value is not None]
    return list_sum(values) if len(values) > 0 else None


def impact_endpoint_value(model: str, term_id: str, impact: dict, lookup_col: str) -> float:
    """
    Calculate the value of the impact based on lookup factors and impacts value.

    Parameters
    ----------
    model : str
        Restrict the impacts by this model.
    term_id : str
        The term to display in the logs only.
    impact_assessment : dict
        The `ImpactAssessment`.
    lookup_col : str
        The lookup column to fetch the factors from.

    Returns
    -------
    int
        The impact total value.
    """
    nodes = [i for i in impact.get('impacts', []) if (
        i.get('methodModel').get('@id') == model or
        not i.get('methodModel').get('@id').startswith(model[0:6])  # allow other non-related models to be accounted for
    )]
    factors = list(map(_factor_value(model, term_id, 'characterisedIndicator.csv', lookup_col), nodes))
    values = [value for value in factors if value is not None]
    return list_sum(values) if len(values) > 0 else None


def emission_value(impact_assessment: dict, term_id: str):
    return find_term_match(impact_assessment.get('emissionsResourceUse', []), term_id).get('value')


def convert_value_from_cycle(product: dict, value: float, default=None):
    pyield = list_sum(product.get('value', [])) if product else 0
    economic_value = product.get('economicValueShare', 0) if product else 0
    return (value / pyield) * economic_value / 100 if value is not None and pyield > 0 else default
