"""
Site

Some ImpactAssessment models need a full version of the linked [Site](https://hestia.earth/schema/Site) to run.
This model will fetch the complete version of the [Site](https://hestia.earth/schema/Site) and include it.
"""
from hestia_earth.schema import SchemaType

from hestia_earth.models.utils import _load_calculated_node

REQUIREMENTS = {
    "ImpactAssessment": {
        "site": {
            "@type": "Site",
            "@id": ""
        }
    }
}
RETURNS = {
    "ImpactAssessment": {
        "site": {"@type": "Site"}
    }
}
MODEL_KEY = 'site'


def _run(impact: dict): return _load_calculated_node(impact.get(MODEL_KEY, {}), SchemaType.SITE)


def _should_run(impact: dict):
    site_id = impact.get(MODEL_KEY, {}).get('@id')
    run = site_id is not None
    return run


def run(impact: dict): return {**impact, **({MODEL_KEY: _run(impact)} if _should_run(impact) else {})}
