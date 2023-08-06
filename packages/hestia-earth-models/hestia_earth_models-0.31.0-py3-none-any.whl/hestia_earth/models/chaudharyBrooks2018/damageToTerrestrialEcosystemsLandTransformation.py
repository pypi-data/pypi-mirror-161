from hestia_earth.schema import IndicatorStatsDefinition

from hestia_earth.models.log import debugValues, logRequirements, logShouldRun
from hestia_earth.models.utils import sum_values, multiply_values
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import (
    convert_value_from_cycle, emission_value, get_product, get_site
)
from hestia_earth.models.utils.input import sum_input_impacts
from .utils import get_region_factor
from . import MODEL

REQUIREMENTS = {
    "ImpactAssessment": {
        "site": {
            "@type": "Site",
            "siteType": "",
            "or": {
                "ecoregion": "",
                "country": {"@type": "Term", "termType": "region"}
            }
        },
        "cycle": {
            "@type": "Cycle",
            "products": [{
                "@type": "Product",
                "primary": "True",
                "value": "> 0",
                "economicValueShare": "> 0"
            }]
        },
        "optional": {
            "emissionsResourceUse": [
                {"@type": "Indicator", "value": "", "term.@id": "landTransformationFromForest20YearAverageDuringCycle"},
                {"@type": "Indicator", "value": "", "term.@id": "landTransformationFromOtherNaturalVegetation20YearAverageDuringCycle"}  # noqa: E501
            ]
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
    "ecoregion-siteType-LandTransformationChaudaryBrooks2018CF": "using `ecoregion`",
    "region-siteType-LandTransformationChaudaryBrooks2018CF": "using `country`"
}
TERM_ID = 'damageToTerrestrialEcosystemsLandTransformation'
LOOKUP_SUFFIX = 'LandTransformationChaudaryBrooks2018CF'
TRANSFORMATION_TERM_IDS = [
    'landTransformationFromForest20YearAverageDuringCycle',
    'landTransformationFromOtherNaturalVegetation20YearAverageDuringCycle'
]


def _indicator(value: float):
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _value(impact_assessment: dict, term_id: str):
    value = emission_value(impact_assessment, term_id)
    debugValues(impact_assessment, model=MODEL, term=TERM_ID, node=term_id, value=value, coefficient=1)
    return value


def _run(impact_assessment: dict):
    cycle = impact_assessment.get('cycle', {})
    product = get_product(impact_assessment)
    landTransformation = sum_values([_value(impact_assessment, term_id) for term_id in TRANSFORMATION_TERM_IDS])
    factor = get_region_factor(TERM_ID, impact_assessment, LOOKUP_SUFFIX, 'medium_intensity')
    inputs_value = convert_value_from_cycle(product, sum_input_impacts(cycle.get('inputs', []), TERM_ID))
    logRequirements(impact_assessment, model=MODEL, term=TERM_ID,
                    landTransformation=landTransformation,
                    factor=factor,
                    inputs_value=inputs_value)
    value = sum_values([
        multiply_values([landTransformation, factor]),
        inputs_value
    ])
    return _indicator(value)


def _should_run(impact_assessment: dict):
    site = get_site(impact_assessment)
    # does not run without a site as data is geospatial
    should_run = all([site])
    logShouldRun(impact_assessment, MODEL, TERM_ID, should_run)
    return should_run


def run(impact_assessment: dict):
    return _run(impact_assessment) if _should_run(impact_assessment) else None
