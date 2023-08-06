import bluebelt
import numpy as np
import pandas as pd
import datetime

from collections.abc import Iterable

from bluebelt.helpers.language import holidays


def _new_years_day(year):
    return pd.Timestamp(datetime.date(year, 1, 1))


def _easter(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
    e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
    f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
    month = f // 31
    day = f % 31 + 1
    return pd.Timestamp(datetime.date(year, month, day))


def _easter_monday(year):
    return pd.Timestamp(_easter(year) + datetime.timedelta(days=1))


def _good_friday(year):
    return pd.Timestamp(_easter(year) + datetime.timedelta(days=-2))


def _ascension_day(year):
    return pd.Timestamp(_easter(year) + datetime.timedelta(days=39))


def _pentecost(year):
    return pd.Timestamp(_easter(year) + datetime.timedelta(days=49))


def _whit_monday(year):
    return pd.Timestamp(_easter(year) + datetime.timedelta(days=50))


def _christmas(year):
    return pd.Timestamp(datetime.date(year, 12, 25))


def _boxing_day(year):
    return pd.Timestamp(datetime.date(year, 12, 26))


def _kings_day(year):
    return pd.Timestamp(datetime.date(year, 4, 27))


def _liberation_day(year, annually=False):
    if annually == True or year % 5 == 0:
        return pd.Timestamp(datetime.date(year, 5, 5))
    else:
        return None


def get_holidays(year, skip=None):

    if isinstance(skip, str):
        skip = [skip]
    if isinstance(skip, list):
        if all(x in holidays.get(bluebelt.config("language")).keys() for x in skip):
            keys = [
                value
                for (key, value) in holidays.get(bluebelt.config("language")).items()
                if key not in skip
            ]
        else:
            raise ValueError(
                f"for the 'skip' option choose from {str(holidays.get(bluebelt.config('language')).keys())}"
            )
    else:
        keys = holidays.get(bluebelt.config("language")).values()

    if isinstance(year, int):
        result = []
        if "_new_years_day" in keys:
            result += [_new_years_day(year)]
        if "_good_friday" in keys:
            result += [_good_friday(year)]
        if "_easter" in keys:
            result += [_easter(year)]
        if "_easter_monday" in keys:
            result += [_easter_monday(year)]
        if "_ascension_day" in keys:
            result += [_ascension_day(year)]
        if "_pentecost" in keys:
            result += [_pentecost(year)]
        if "_whit_monday" in keys:
            result += [_whit_monday(year)]
        if "_christmas" in keys:
            result += [_christmas(year)]
        if "_boxing_day" in keys:
            result += [_boxing_day(year)]
        if "_kings_day" in keys:
            result += [_kings_day(year)]
        if "_liberation_day" in keys and _liberation_day(year):
            result += [_liberation_day(year)]
        return result
    elif isinstance(year, list):
        result = []
        for this_year in year:
            result += get_holidays(this_year, skip=skip)
        return result
    else:
        return []


def get_holidays_dict(year, skip=None, result=None):

    if isinstance(skip, str):
        skip = [skip]
    if isinstance(skip, list):
        if all(x in holidays.get(bluebelt.config("language")).keys() for x in skip):
            keys = [
                value
                for (key, value) in holidays.get(bluebelt.config("language")).items()
                if key not in skip
            ]
        else:
            raise ValueError(
                f"for the 'skip' option choose from {str(holidays.get(bluebelt.config('language')).keys())}"
            )
    else:
        keys = holidays.get(bluebelt.config("language")).values()

    # if not isinstance(year, int):
    #     raise ValueError("Please provide a single year to get the holidays dict")

    result = result or {}
    if isinstance(year, int):
        if "_new_years_day" in keys:
            result[_new_years_day(year)] = "new_years_day"
        if "_good_friday" in keys:
            result[_good_friday(year)] = "good_friday"
        if "_easter" in keys:
            result[_easter(year)] = "easter"
        if "_easter_monday" in keys:
            result[_easter_monday(year)] = "easter_monday"
        if "_ascension_day" in keys:
            result[_ascension_day(year)] = "ascension_day"
        if "_pentecost" in keys:
            result[_pentecost(year)] = "pentecost"
        if "_whit_monday" in keys:
            result[_whit_monday(year)] = "whit_monday"
        if "_christmas" in keys:
            result[_christmas(year)] = "christmas"
        if "_boxing_day" in keys:
            result[_boxing_day(year)] = "boxing_day"
        if "_kings_day" in keys:
            result[_kings_day(year)] = "kings_day"
        if "_liberation_day" in keys and _liberation_day(year):
            result[_liberation_day(year)] = "liberation_day"

        return result

    elif isinstance(year, Iterable):
        for this_year in year:
            result = get_holidays_dict(this_year, skip=skip, result=result)
        return result
    else:
        return {}
