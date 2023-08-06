"""
ecoinvent v3

This model calculates background emissions related to the production of Inputs from the ecoinvent database, version 3.
"""
from functools import reduce
from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.tools import flatten, list_sum, non_empty_list

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.data.impact_assessment import ecoinventV3_impacts
from hestia_earth.models.utils.emission import _new_emission

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{"@type": "Input", "value": "> 0"}]
    }
}
RETURNS = {
    "Emission": [{
        "term": "",
        "value": "",
        "methodTier": "background",
        "inputs": ""
    }]
}
MODEL = 'ecoinventV3'
MODEL_KEY = 'impactAssessment'  # keep to generate entry in "model-links.json"
TIER = EmissionMethodTier.BACKGROUND.value


def _emission(term_id: str, value: float, input: dict):
    emission = _new_emission(term_id, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    emission['inputs'] = [input.get('term')]
    if input.get('operation'):
        emission['operation'] = input.get('operation')
    return emission


def _add_emission(input: dict):
    def add(prev: dict, mapping: tuple):
        ecoinventName, coefficient = mapping
        emissions = ecoinventV3_impacts(ecoinventName)
        for id, value in emissions:
            # log run on each emission so we know it did run
            debugValues(input, model=MODEL, term=id, value=value, coefficient=coefficient)
            prev[id] = prev.get(id, 0) + (value * coefficient)
        return prev
    return add


def _get_input_mappings(cycle: dict, input: dict):
    term = input.get('term', {})
    term_id = term.get('@id')
    value = get_lookup_value(term, 'ecoinventMapping', model=MODEL, term=term_id)
    mappings = non_empty_list(value.split(';')) if value else []
    logRequirements(cycle, model=MODEL, term=term_id,
                    mappings=';'.join(mappings))
    return [(m.split(':')[0], float(m.split(':')[1])) for m in mappings]


def _run_input(cycle: dict):
    def run(inputs: list):
        input = inputs[0]
        input_value = list_sum(flatten(input.get('value', []) for input in inputs))
        mappings = _get_input_mappings(cycle, input)
        term_id = input.get('term', {}).get('@id')
        should_run = len(mappings) > 0
        logShouldRun(cycle, MODEL, term_id, should_run, methodTier=TIER)
        grouped_emissions = reduce(_add_emission(input), mappings, {}) if should_run else {}
        return [_emission(term_id, value * input_value, input) for term_id, value in grouped_emissions.items()]
    return run


def _group_inputs(group: dict, input: dict):
    term_id = input.get('term', {}).get('@id')
    group[term_id] = group.get(term_id, []) + [input]
    return group


def run(cycle: dict):
    inputs = [i for i in cycle.get('inputs', []) if list_sum(i.get('value', [])) > 0]
    inputs = reduce(_group_inputs, inputs, {})
    # group inputs with same id to avoid adding emissions twice
    return flatten(map(_run_input(cycle), inputs.values()))
