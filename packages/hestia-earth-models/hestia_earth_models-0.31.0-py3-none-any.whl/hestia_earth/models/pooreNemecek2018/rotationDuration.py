from hestia_earth.schema import PracticeStatsDefinition
from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logShouldRun
from hestia_earth.models.utils.practice import _new_practice
from . import MODEL
from .orchardDuration import _get_value as get_orchardDuration
from .longFallowPeriod import _get_value as get_longFallowPeriod

REQUIREMENTS = {
    "Cycle": {
        "products": [{"@type": "Product", "value": "", "term.termType": "crop"}],
        "site": {
            "@type": "Site",
            "siteType": "cropland"
        }
    }
}
LOOKUPS = {
    "crop": ["Orchard_duration", "Orchard_longFallowPeriod"]
}
RETURNS = {
    "Practice": [{
        "value": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'rotationDuration'


def _get_value(product: dict):
    orchardDuration = get_orchardDuration(product)
    longFallowPeriod = get_longFallowPeriod(product)
    return orchardDuration + longFallowPeriod if orchardDuration is not None and longFallowPeriod is not None else None


def _practice(value: float):
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [value]
    practice['statsDefinition'] = PracticeStatsDefinition.MODELLED.value
    return practice


def run(cycle: dict):
    def run_product(product):
        value = _get_value(product)
        should_run = value is not None
        logShouldRun(product, MODEL, TERM_ID, should_run)
        return _practice(value) if should_run else None

    return non_empty_list(map(run_product, cycle.get('products', [])))
