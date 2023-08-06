"""
Compute Annual value based on Monthly values.
"""
from hestia_earth.schema import MeasurementStatsDefinition
from hestia_earth.utils.tools import flatten

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement
from .utils import _slice_by_year
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "measurements": [
            {"@type": "Measurement", "term.id": "precipitationMonthly"}
        ]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "startDate": "",
        "endDate": "",
        "statsDefinition": "modelled"
    }]
}
TERM_ID = 'precipitationAnnual'
MEASUREMENT_ID = 'precipitationMonthly'


def _measurement(value: float, start_date: str, end_date: str):
    measurement = _new_measurement(TERM_ID)
    measurement['value'] = [value]
    measurement['startDate'] = start_date
    measurement['endDate'] = end_date
    measurement['statsDefinition'] = MeasurementStatsDefinition.MODELLED.value
    return measurement


def _run(measurement: dict):
    values = measurement.get('value', [])
    dates = measurement.get('dates', [])
    term_id = measurement.get('term', {}).get('@id')
    results = _slice_by_year(term_id, dates, values)
    return [_measurement(value, start_date, end_date) for (value, start_date, end_date) in results]


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
