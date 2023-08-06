import bluebelt
import pandas as pd
import numpy as np
import datetime
import bluebelt.helpers.date
import bluebelt.helpers.language

from collections.abc import Iterable


def _series_function(x):
    function = (
        np.random.uniform(low=0.000014, high=0.000018)
        * (x - np.random.uniform(low=150, high=200)) ** 3
        - np.random.uniform(low=0.0002, high=0.0004)
        * (x - np.random.uniform(low=500, high=750)) ** 2
        - np.random.uniform(low=0.2, high=0.8) * x
        + np.random.uniform(low=500, high=600)
    )
    return function


def series(
    years: int = 1, resolution: float = 0.25, frac: float = 0.02, name: str = "hours"
) -> pd.Series:

    # get the current year
    this_year = datetime.datetime.now().isocalendar()[0]

    # trends
    trends = np.random.normal(loc=1, scale=0.1, size=years)

    data = []

    for year in range(years - 1, -1, -1):
        start_date = datetime.datetime.fromisocalendar(this_year - year, 1, 1)

        nrows = bluebelt.helpers.date.last_iso_week_in_year(this_year - year) * 7
        series = pd.Series(
            data=np.array(list(map(_series_function, np.arange(0, nrows))))
            + (
                np.random.normal(
                    loc=100 * trends[year], scale=4 * trends[year], size=nrows
                )
            ),
            index=pd.date_range(start=start_date, periods=nrows),
        )

        # week & month pattern
        w = pd.Series(
            data=[1.09, 1.05, 0.96, 0.97, 1.11, 0.32, 0.05] * int(nrows / 7),
            index=pd.date_range(start=start_date, periods=nrows),
        )
        m = pd.Series(
            data=series.index.day.map(
                {27: 1.03, 28: 1.06, 29: 1.11, 30: 1.16, 31: 1.09}
            ).fillna(1),
            index=pd.date_range(start=start_date, periods=nrows),
        )

        # set to startpoint
        if year < years - 1:
            series = series + startpoint - series[0]
        startpoint = series[-1]

        series = series.multiply(w).multiply(m)

        # apply resolution
        series = series.divide(resolution).round().multiply(resolution)

        series = series.rename(name)

        data += [series]

    series = pd.concat(data, axis=0)

    # break the series
    series.loc[series.sample(frac=frac).index] = np.nan

    return series


def frame(
    years: int = 1, skills: int = 4, resolution: float = 0.25, frac: float = 0.02
) -> pd.DataFrame:
    data = []
    for skill in range(skills):
        data += [
            series(
                years=years,
                resolution=resolution,
                frac=frac,
                name="skill " + chr(ord("A") + skill),
            )
        ]

    frame = pd.concat(data, axis=1)

    return frame


def holiday_dict(values=None):

    hd = bluebelt.helpers.language.holidays.get(bluebelt.get_language())

    if isinstance(values, Iterable) and (len(values) != len(hd.keys())):
        values = (values * len(hd.keys()))[: len(hd.keys())]

    if isinstance(values, str) or not isinstance(values, Iterable):
        values = [values] * len(hd.keys())

    return {key: values[id] for id, key in enumerate(hd.keys())}


def holiday_list():

    hd = bluebelt.helpers.language.holidays.get(bluebelt.get_language())

    return [val for val in hd.keys()]
