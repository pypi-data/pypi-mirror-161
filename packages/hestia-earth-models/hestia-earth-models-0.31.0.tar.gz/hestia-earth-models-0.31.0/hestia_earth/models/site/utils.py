from functools import reduce
import datetime
from hestia_earth.schema import TermTermType
from hestia_earth.utils.tools import non_empty_list
from hestia_earth.utils.date import DAY

from hestia_earth.models.utils.measurement import measurement_value


def _has_all_months(dates: list):
    try:
        months = [int(d[5:7]) for d in dates]
        return all(m in months for m in range(1, 13))
    except Exception:
        return False


def _slice_by_year(term_id: str, dates: list, values: list):
    def group_values(group: dict, index: int):
        date = dates[index]
        value = values[index]
        month = dates[index][0:4]
        group[month] = group.get(month, []) + [(date, value)]
        return group

    def iterate_values(data: list):
        return (
            measurement_value({
                'term': {
                    '@id': term_id,
                    'termType': TermTermType.MEASUREMENT.value
                },
                'value': non_empty_list([v for (_d, v) in data])
            }, is_larger_unit=True),
            data[0][0],
            data[-1][0]
        ) if _has_all_months([d for (d, _v) in data]) else None

    values_by_month = reduce(group_values, range(0, len(dates)), {})
    return non_empty_list(map(iterate_values, values_by_month.values()))


def _extract_year_month(date: str):
    try:
        year = int(date[0:4])
        month = int(date[5:7])
        return year, month
    except Exception:
        return None, None


def _group_by_month(term_id: str, dates: list, values: list):
    def group_values(group: dict, index: int):
        date = dates[index]
        value = values[index]
        month = dates[index][0:7]
        group[month] = group.get(month, []) + [(date, value)]
        return group

    def map_to_month(data: list, year: int, month: int):
        # make sure we got all the necessary days
        first_day_of_month = datetime.date(year, month, 1)
        last_day_of_month = datetime.date(year + int(month / 12), (month % 12) + 1, 1) - datetime.timedelta(days=1)

        difference = last_day_of_month - first_day_of_month
        days_in_month = round(difference.days + difference.seconds / DAY, 1) + 1

        return measurement_value({
            'term': {
                '@id': term_id,
                'termType': TermTermType.MEASUREMENT.value
            },
            'value': non_empty_list([v for (_d, v) in data])
        }, is_larger_unit=True) if len(data) == days_in_month else None

    values_by_month = reduce(group_values, range(0, len(dates)), {})

    values = []
    dates = []
    for month, data in values_by_month.items():
        year, m = _extract_year_month(data[0][0])
        # date might not contain a year or a month, cannot handle it
        value = map_to_month(data, year, m) if year and m else None
        if value is not None:
            dates.append(month)
            values.append(value)

    return values, dates
