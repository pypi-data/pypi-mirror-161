import numpy as np
import pandas as pd

import bluebelt.helpers.date

import datetime


def project(_obj, year=None, adjust_holidays=True):

    _obj = _obj.copy()

    # check if _obj has only one iso year
    if _obj.index.isocalendar().year.unique().size > 1:
        raise ValueError("The _obj can only contain one iso year")

    # check for week 53
    if (
        _obj.index.isocalendar().week.max()
        > bluebelt.helpers.date.last_iso_week_in_year(year)
    ):
        # drop week 53
        _obj = _obj[_obj.index.isocalendar().week < 53]
    elif (
        _obj.index.isocalendar().week.max()
        < bluebelt.helpers.date.last_iso_week_in_year(year)
    ):
        # create week 53
        pass

    # create a isoformat MultiIndex
    index = pd.MultiIndex.from_frame(_obj.index.isocalendar())
    # set the year to the requested year
    index = index.set_levels([year], level=0)
    # build a new DatetimeIndex from the isoformat MultiIndex
    index = pd.DatetimeIndex(
        np.apply_along_axis(
            lambda x: datetime.datetime.fromisocalendar(x[0], x[1], x[2]),
            1,
            np.array([*index.values]),
        )
    )
    # create the new _obj
    if isinstance(_obj, pd.Series):
        result = pd.Series(index=index, data=_obj.values, name=_obj.name)
    else:
        result = pd.DataFrame(index=index, data=_obj.values, columns=_obj.columns)

    if adjust_holidays:

        # get original holidays
        _obj_holidays = bluebelt.helpers.holidays.get_holidays_dict(
            _obj.index.year.unique()
        )
        # find the new dates for the original holidays
        _obj_holidays = {
            datetime.datetime.fromisocalendar(
                year, key.isocalendar()[1], key.isocalendar()[2]
            ): value
            for key, value in _obj_holidays.items()
            if key in _obj.index
        }

        # get new holidays
        result_holidays = bluebelt.helpers.holidays.get_holidays_dict(
            result.index.year.unique()
        )
        result_holidays = {
            value: key for key, value in result_holidays.items() if key in result.index
        }

        # create a swap dictionairy
        holidays = {
            key: result_holidays.get(value) for key, value in _obj_holidays.items()
        }

        for key, value in holidays.items():

            # catch none existing holidays like liberation day in some years
            if key and value:
                result.loc[[key, value]] = result.loc[[value, key]].values

    return result
