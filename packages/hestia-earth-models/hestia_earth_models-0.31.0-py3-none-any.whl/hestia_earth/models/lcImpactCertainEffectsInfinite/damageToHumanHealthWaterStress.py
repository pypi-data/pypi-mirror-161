from hestia_earth.schema import IndicatorStatsDefinition

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils import sum_values
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import (
    convert_value_from_cycle, get_product, impact_country_value, impact_aware_value
)
from hestia_earth.models.utils.input import sum_input_impacts
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "emissionsResourceUse": [{"@type": "Indicator", "value": "", "term.termType": "resourceUse"}],
        "site": {
            "@type": "Site",
            "or": {
                "awareWaterBasinId": "",
                "country": {"@type": "Term", "termType": "region"}
            }
        }
    }
}
RETURNS = {
    "Indicator": {
        "value": "",
        "statsDefinition": "modelled"
    }
}
LOOKUPS = {
    "@doc": "Different lookup files are used depending on the situation",
    "awareWaterBasinId-resourceUse-WaterStressDamageToHumanHealthLCImpactCF": "using `awareWaterBasinId`",
    "region-resourceUse-WaterStressDamageToHumanHealthLCImpactCF": "using `region`"
}
TERM_ID = 'damageToHumanHealthWaterStress'
LOOKUP_SUFFIX = 'resourceUse-WaterStressDamageToHumanHealthLCImpactCF'


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def run(impact_assessment: dict):
    cycle = impact_assessment.get('cycle', {})
    product = get_product(impact_assessment)
    value = impact_aware_value(
        MODEL, TERM_ID,
        impact_assessment,
        f"awareWaterBasinId-{LOOKUP_SUFFIX}.csv"
    ) or impact_country_value(
        MODEL, TERM_ID,
        impact_assessment,
        f"region-{LOOKUP_SUFFIX}.csv"
    )
    inputs_value = convert_value_from_cycle(product, sum_input_impacts(cycle.get('inputs', []), TERM_ID), None)
    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    value=value,
                    inputs_value=inputs_value)
    logShouldRun(impact_assessment, MODEL, TERM_ID, True)
    return _indicator(sum_values([value, inputs_value]))
