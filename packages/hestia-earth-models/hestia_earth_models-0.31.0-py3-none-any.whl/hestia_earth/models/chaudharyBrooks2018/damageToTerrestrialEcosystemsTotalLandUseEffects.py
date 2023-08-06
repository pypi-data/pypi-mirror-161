from hestia_earth.schema import IndicatorStatsDefinition
from hestia_earth.utils.tools import list_sum, safe_parse_float, non_empty_list
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils import sum_values
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import convert_value_from_cycle, get_product
from hestia_earth.models.utils.input import sum_input_impacts
from .damageToTerrestrialEcosystemsLandOccupation import TERM_ID as TERM_ID_1
from .damageToTerrestrialEcosystemsLandTransformation import TERM_ID as TERM_ID_2
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "cycle": {
            "@type": "Cycle",
            "products": [{
                "@type": "Product",
                "primary": "True",
                "value": "> 0",
                "economicValueShare": "> 0"
            }]
        },
        "impacts": [
            {"@type": "Indicator", "value": "", "term.@id": "damageToTerrestrialEcosystemsLandOccupation"},
            {"@type": "Indicator", "value": "", "term.@id": "damageToTerrestrialEcosystemsLandTransformation"}
        ]
    }
}
RETURNS = {
    "Indicator": {
        "value": "",
        "statsDefinition": "modelled"
    }
}
TERM_ID = 'damageToTerrestrialEcosystemsTotalLandUseEffects'
BIODIVERSITY_TERM_IDS = [TERM_ID_1, TERM_ID_2]


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def impact_value(impact_assessment: dict, term_id: str):
    impact = find_term_match(impact_assessment.get('impacts', []), term_id)
    value = impact.get('value')
    value = safe_parse_float(value) if value else None
    debugValues(impact, model=MODEL, term=TERM_ID, node=term_id, value=value, coefficient=1)
    return value


def run(impact_assessment: dict):
    landUseEffects = list_sum(non_empty_list(
        [impact_value(impact_assessment, term_id) for term_id in BIODIVERSITY_TERM_IDS]
    ), None)
    cycle = impact_assessment.get('cycle', {})
    product = get_product(impact_assessment)
    inputs_value = convert_value_from_cycle(product, sum_input_impacts(cycle.get('inputs', []), TERM_ID))
    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    landUseEffects=landUseEffects,
                    inputs_value=inputs_value)
    logShouldRun(impact_assessment, MODEL, TERM_ID, True)
    return _indicator(sum_values([landUseEffects, inputs_value]))
