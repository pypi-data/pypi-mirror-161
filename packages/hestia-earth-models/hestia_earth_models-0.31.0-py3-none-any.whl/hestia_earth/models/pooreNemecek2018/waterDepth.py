from hestia_earth.schema import MeasurementStatsDefinition, SiteSiteType

from hestia_earth.models.log import logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement
from . import MODEL

REQUIREMENTS = {
    "Site": {}
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "statsDefinition": "modelled"
    }]
}
LOOKUPS = {
    "crop": "Non_bearing_duration"
}
TERM_ID = 'waterDepth'
SITE_TYPE_TO_DEPTH = {
    SiteSiteType.POND.value: 1.5,
    SiteSiteType.RIVER_OR_STREAM.value: 1,
    SiteSiteType.LAKE.value: 20,
    SiteSiteType.SEA_OR_OCEAN.value: 40
}


def measurement(value: float):
    measurement = _new_measurement(TERM_ID, MODEL)
    measurement['value'] = [value]
    measurement['statsDefinition'] = MeasurementStatsDefinition.MODELLED.value
    return measurement


def _run(site: dict):
    logShouldRun(site, MODEL, TERM_ID, True)
    site_type = site.get('siteType')
    value = SITE_TYPE_TO_DEPTH.get(site_type, 0)
    return measurement(value) if value else None


def run(site: dict): return _run(site)
