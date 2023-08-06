"""
Input Properties

This model adds properties to the `Input` when they are connected to another `Cycle` via the
[impactAssessment](https://hestia.earth/schema/Input#impactAssessment) field.
"""
from hestia_earth.schema import SchemaType
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.utils import _load_calculated_node

REQUIREMENTS = {
    "Cycle": {
        "inputs": [{
            "@type": "Input",
            "impactAssessment": ""
        }]
    }
}
RETURNS = {
    "Inputs": [{
        "properties": [{
            "@type": "Property"
        }]
    }]
}
MODEL_KEY = 'properties'


def _run_input(values: tuple):
    input, properties = values
    existing_properties = input.get('properties', [])
    new_properties = [p for p in properties if not find_term_match(existing_properties, p.get('term', {}).get('@id'))]
    return {**input, 'properties': existing_properties + new_properties}


def _input_properties(input: dict):
    impact = input.get('impactAssessment')
    impact = _load_calculated_node(impact, SchemaType.IMPACTASSESSMENT) if impact else {}
    cycle = impact.get('cycle')
    products = (_load_calculated_node(cycle, SchemaType.CYCLE) if cycle else {}).get('products', [])
    return find_term_match(products, input.get('term', {}).get('@id')).get('properties', [])


def run(cycle: dict):
    # select inputs which have corresponding properties
    inputs = [(i, _input_properties(i)) for i in cycle.get('inputs', [])]
    inputs = [(input, properties) for input, properties in inputs if len(properties) > 0]
    return list(map(_run_input, inputs))
