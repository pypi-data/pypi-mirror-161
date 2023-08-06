from hestia_earth.schema import IndicatorStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import convert_value_from_cycle, get_product
from hestia_earth.models.utils.cycle import impact_lookup_value as cycle_lookup_value
from hestia_earth.models.utils.input import sum_input_impacts
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "cycle": {
            "@type": "Cycle",
            "dataCompleteness.electricityFuel": "True",
            "inputs": [{"@type": "Input", "value": "", "term.termType": "fuel"}]
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
    "fuel": "oilEqHierarchistFossilResourceScarcityReCiPe2016"
}
TERM_ID = 'fossilResourceScarcity'


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def run(impact_assessment: dict):
    cycle = impact_assessment.get('cycle', {})
    product = get_product(impact_assessment)
    is_complete = cycle.get('dataCompleteness', {}).get('electricityFuel', False)
    product = get_product(impact_assessment)
    fuels = filter_list_term_type(cycle.get('inputs', []), TermTermType.FUEL)
    has_fuels = len(fuels) > 0
    fuels_value = convert_value_from_cycle(
        product, cycle_lookup_value(MODEL, TERM_ID, fuels, LOOKUPS['fuel']), None
    )
    inputs_value = convert_value_from_cycle(product, sum_input_impacts(cycle.get('inputs', []), TERM_ID), None)
    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    is_complete=is_complete,
                    has_fuels=has_fuels,
                    fuels_value=fuels_value,
                    inputs_value=inputs_value)

    should_run = any([
        is_complete and not has_fuels,
        is_complete and fuels_value is not None
    ])
    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)

    return _indicator(
        (fuels_value or 0) + (inputs_value or 0)
    ) if should_run else None
