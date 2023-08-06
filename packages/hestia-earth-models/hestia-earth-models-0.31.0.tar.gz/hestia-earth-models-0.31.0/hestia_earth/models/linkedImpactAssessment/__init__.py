"""
Linked Impact Assessment

A model which takes recalculated data from an Impact Assessment linked to an Input in a Cycle.
"""
from functools import reduce
from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import flatten, list_sum

from hestia_earth.models.log import logRequirements, logShouldRun, logger
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import load_impacts

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{
            "@type": "Input",
            "value": "> 0",
            "impactAssessment": ""
        }]
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "background",
        "statsDefinition": "modelled",
        "inputs": ""
    }]
}
MODEL = 'linkedImpactAssessment'
MODEL_AGGREGATED = 'hestiaAggregatedData'
TIER = EmissionMethodTier.BACKGROUND.value


def _emission(term_id: str, value: float, input: dict, model: str):
    # log run on each emission so we know it did run
    logShouldRun(input, model, term_id, True, methodTier=TIER)
    value = list_sum(input.get('value', [0])) * value
    emission = _new_emission(term_id, model)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    emission['inputs'] = [input.get('term')]
    if input.get('operation'):
        emission['operation'] = input.get('operation')
    return emission


def _emission_group(term_id: str):
    lookup = download_lookup('emission.csv', True)
    return get_table_value(lookup, 'termid', term_id, column_name('inputProductionGroupId'))


def _group_emissions(impact: dict):
    def _group_by(prev: dict, emission: dict):
        term_id = emission.get('term', {}).get('@id')
        grouping = _emission_group(term_id)
        if grouping:
            prev[grouping] = prev.get(grouping, 0) + (emission.get('value', 0) or 0)
        return prev

    emissions = impact.get('emissionsResourceUse', [])
    return reduce(_group_by, emissions, {})


def _run_input(cycle: dict):
    def exec(input: dict):
        term_id = input.get('term', {}).get('@id')
        impact = input.get('impactAssessment')
        model = MODEL_AGGREGATED if impact.get('aggregated', False) else MODEL
        emissions = _group_emissions(impact)
        logRequirements(cycle, model=model, term=term_id,
                        impact_assessment_id=input.get('impactAssessment', {}).get('@id'))
        logShouldRun(cycle, model, term_id, True, methodTier=TIER)
        return [
            _emission(id, value, input, model) for id, value in emissions.items()
        ]
    return exec


def run(_, cycle: dict):
    inputs = load_impacts(cycle.get('inputs', []))
    inputs = [i for i in inputs if list_sum(i.get('value', [])) > 0]
    logger.debug('model=%s, nb inputs=%s', MODEL, len(inputs))
    return flatten(map(_run_input(cycle), inputs))
