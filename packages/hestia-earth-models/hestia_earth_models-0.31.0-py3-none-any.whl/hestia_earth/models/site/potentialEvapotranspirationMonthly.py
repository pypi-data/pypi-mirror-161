"""
Compute Monthly value based on Daily values.
"""
from hestia_earth.schema import MeasurementStatsDefinition
from hestia_earth.utils.tools import flatten

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement
from .utils import _group_by_month
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "measurements": [
            {"@type": "Measurement", "term.id": "potentialEvapotranspirationDaily"}
        ]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "dates": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'potentialEvapotranspirationMonthly'
MEASUREMENT_ID = 'potentialEvapotranspirationDaily'


def _measurement(value: list, dates: list):
    measurement = _new_measurement(TERM_ID)
    measurement['value'] = value
    measurement['dates'] = dates
    measurement['statsDefinition'] = MeasurementStatsDefinition.MODELLED.value
    return measurement


def _run(measurement: dict):
    values = measurement.get('value', [])
    dates = measurement.get('dates', [])
    term_id = measurement.get('term', {}).get('@id')
    result = _group_by_month(term_id, dates, values)
    return _measurement(result[0], result[1]) if len(result[0]) > 0 else None


def _should_run(site: dict):
    measurements = [m for m in site.get('measurements', []) if m.get('term', {}).get('@id') == MEASUREMENT_ID]
    has_daily_measurements = len(measurements) > 0

    logRequirements(site, model=MODEL, term=TERM_ID,
                    has_daily_measurements=has_daily_measurements)

    should_run = all([has_daily_measurements])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run, measurements


def run(site: dict):
    should_run, measurements = _should_run(site)
    return flatten(map(_run, measurements)) if should_run else []
