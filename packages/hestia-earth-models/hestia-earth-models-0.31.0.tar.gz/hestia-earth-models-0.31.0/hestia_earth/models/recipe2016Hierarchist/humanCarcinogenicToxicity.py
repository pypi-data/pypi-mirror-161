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
            "dataCompleteness.pesticidesAntibiotics": "True",
            "inputs": [{"@type": "Input", "value": "", "term.termType": "pesticideAI"}]
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
    "pesticideAI": "14DCBeqHierarchistHumanCarcinogenicToxicityReCiPe2016"
}
TERM_ID = 'humanCarcinogenicToxicity'


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def run(impact_assessment: dict):
    cycle = impact_assessment.get('cycle', {})
    is_complete = cycle.get('dataCompleteness', {}).get('pesticidesAntibiotics', False)
    product = get_product(impact_assessment)
    pesticides = filter_list_term_type(cycle.get('inputs', []), TermTermType.PESTICIDEAI)
    has_pesticides = len(pesticides) > 0
    pesticides_value = convert_value_from_cycle(
        product, cycle_lookup_value(MODEL, TERM_ID, pesticides, LOOKUPS['pesticideAI'], False), None
    )
    inputs_value = convert_value_from_cycle(product, sum_input_impacts(cycle.get('inputs', []), TERM_ID), None)
    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    is_complete=is_complete,
                    has_pesticides=has_pesticides,
                    pesticides_value=pesticides_value,
                    inputs_value=inputs_value)

    should_run = any([
        is_complete and not has_pesticides,
        is_complete and pesticides_value is not None
    ])
    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)

    return _indicator(
        (pesticides_value or 0) + (inputs_value or 0)
    ) if should_run else None
