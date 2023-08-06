from multiprocessing.sharedctypes import Value
import numpy as np
import pandas as pd
import datetime
import math

import bluebelt.helpers.check as check


def resolution_methods(cls):
    def sum(self):

        result = self.grouped.sum(min_count=1)
        if isinstance(self, Flatten):
            result = result.reindex_like(self._obj, method="ffill")
        return result

    def mean(self):
        result = self.grouped.mean()
        if isinstance(self, Flatten):
            result = result.reindex_like(self._obj, method="ffill")
        return result

    def var(self):
        result = self.grouped.var()
        if isinstance(self, Flatten):
            result = result.reindex_like(self._obj, method="ffill")
        return result

    def std(self):
        result = self.grouped.std()
        if isinstance(self, Flatten):
            result = result.reindex_like(self._obj, method="ffill")
        return result

    def min(self):
        result = self.grouped.min()
        if isinstance(self, Flatten):
            result = result.reindex_like(self._obj, method="ffill")
        return result

    def max(self):
        result = self.grouped.max()
        if isinstance(self, Flatten):
            result = result.reindex_like(self._obj, method="ffill")
        return result

    def count(self):
        result = self.grouped.count()
        if isinstance(self, Flatten):
            result = result.reindex_like(self._obj, method="ffill")
        return result

    def value_range(self):
        result = self.grouped.apply(lambda x: x.max() - x.min())
        if isinstance(self, Flatten):
            result = result.reindex_like(self._obj, method="ffill")
        return result

    def subseries(self, count, size=1):
        """
        Count the number of times a list of 'count' items with size 'size' fit
        in each group.

        Parameters
        ----------
        self : GroupBy or Resampling object
        count: int
            The length of the sub-series.
        size: int
            The size of each element in the sub-series.

        Returns
        -------
        Series

        Example
        -------

        GroupBy or Resampling object: pd.Series([10, 8, 3, 3, 5])
        count: 3
        size: 1

        frame.blue.resample(rule=7).subseries(3, 1)
        >>> 9

        Every step subtracts (1, 1, 1, 0, 0), (1, 1, 0, 1, 0), (1, 1, 0, 0, 1),
        (1, 0, 0, 1, 1) or (0, 0, 1, 1, 1) from the group.

        step 0: (3, 3, 5, 8, 10)
        step 1: (3, 3, 4, 7, 9)
        step 2: (3, 3, 3, 6, 8)
        step 3: (2, 3, 3, 5, 7)
        step 4: (2, 2, 3, 4, 6)
        step 5: (2, 2, 2, 3, 5)
        step 6: (1, 2, 2, 2, 4)
        step 7: (1, 1, 1, 2, 3)
        step 8: (0, 1, 1, 1, 2)
        step 9: (0, 0, 0, 1, 1)
        """

        if not isinstance(count, int):
            raise ValueError("count must be an int")
        if not isinstance(size, (float, int)):
            raise ValueError("size must be float or int")
        # if isinstance(self._obj, pd.DataFrame):
        #     data = self._obj.sum(axis=1, numeric_only=True)

        def _subseries_count(series, count=3, size=1):
            # helper for resample.subseries
            series = pd.Series(series) / size
            result = series.sum() * count
            for i in range(count, 0, -1):
                result = np.minimum(
                    result,
                    math.floor(series.nsmallest(len(series) - count + i).sum() / i),
                )
            return result

        if isinstance(self._obj, pd.Series):
            result = pd.Series(
                index=self.grouped.groups.keys(),
                data=self.grouped.apply(
                    lambda x: _subseries_count(series=x, count=count, size=size)
                ).values,
                name=f"subseries {str(count)} of {str(size)}",
            )
        elif isinstance(self._obj, pd.DataFrame):
            result = pd.DataFrame(
                index=self.grouped.groups.keys(),
                data=self.grouped.apply(
                    lambda x: _subseries_count(series=x, count=count, size=size),
                ).values,
                columns=self._obj.columns,
            )

        if isinstance(self, Flatten):
            result = result.reindex_like(self._obj, method="ffill")
        return result

    def diff_quantity(self, skip_na=True, skip_zero=True):
        # if this week > last week: this week - last week / this week
        # if this week < last week: last week - this week / last week

        if isinstance(self._obj, pd.DataFrame):
            data = self._obj.sum(
                axis=1, min_count=1
            )  # min_count=1 prevents np.nan values to become zeros
        else:
            data = self._obj

        # resample the data and transpose into a DataFrame with weekdays as columns
        data = data.resample(rule=self.rule, origin=self.origin, **self.kwargs)
        data = data.apply(
            lambda x: pd.DataFrame(
                index=x.index.isocalendar().day,
                data=x.values,
            ).transpose()
        )

        # drop the extra index level that was created in the transpose
        data = data.droplevel(-1)

        # get the difference, but only for days where both weeks have a proper value
        if skip_na and skip_zero:
            result = (
                data[(data.shift().notna()) & (data.shift() != 0)]
                - data.shift()[(data.notna()) & (data != 0)]
            ).sum(axis=1).abs() / np.maximum(
                data[(data.shift().notna()) & (data.shift() != 0)].sum(axis=1),
                data.shift()[(data.notna()) & (data != 0)].sum(axis=1),
            )
        elif skip_na:
            result = (data[data.shift().notna()] - data.shift()[data.notna()]).sum(
                axis=1
            ).abs() / np.maximum(
                data[data.shift().notna()].sum(axis=1),
                data.shift()[data.notna()].sum(axis=1),
            )
        elif skip_zero:
            result = (data[data.shift() != 0] - data.shift()[data != 0]).sum(
                axis=1
            ).abs() / np.maximum(
                data[data.shift() != 0].sum(axis=1), data.shift()[data != 0].sum(axis=1)
            )
        else:
            result = (data - data.shift()).sum(axis=1).abs() / np.maximum(
                data.sum(axis=1), data.shift().sum(axis=1)
            )

        return result

    def diff_distribution(self, skip_na=True, skip_zero=True):
        # only works with resample('1w') or equivalent
        if self.rule != datetime.timedelta(days=7):
            raise ValueError(
                f"The object must be resampled to weekly data not {self.rule}"
            )

        # if a DataFrame is passed then sum the columns
        if isinstance(self._obj, pd.DataFrame):
            data = self._obj.sum(axis=1, numeric_only=True)
        else:
            data = self._obj

        # resample the data and transpose into a DataFrame with weekdays as columns
        data = data.resample(rule=self.rule, origin=self.origin, **self.kwargs)
        data = data.apply(
            lambda x: pd.DataFrame(
                index=x.index.isocalendar().day,
                data=x.values,
            ).transpose()
        )

        # drop the extra index level that was created in the transpose
        data = data.droplevel(-1)

        # get diff_quantity to calculate the relative difference
        if skip_na and skip_zero:
            diff = (
                (
                    data[(data.shift().notna()) & (data.shift() != 0)]
                    - data.shift()[(data.notna()) & (data != 0)].multiply(
                        data[(data.shift().notna()) & (data.shift() != 0)].sum(axis=1)
                        / data.shift()[(data.notna()) & (data != 0)].sum(axis=1),
                        axis=0,
                    )
                )
                .abs()
                .sum(axis=1, min_count=1)
            )
        elif skip_na:
            diff = (
                (
                    data[data.shift().notna()]
                    - data.shift()[data.notna()].multiply(
                        data[data.shift().notna()].sum(axis=1)
                        / data.shift()[data.notna()].sum(axis=1),
                        axis=0,
                    )
                )
                .abs()
                .sum(axis=1, min_count=1)
            )
        elif skip_zero:
            diff = (
                (
                    data[data.shift() != 0]
                    - data.shift()[data != 0].multiply(
                        data[data.shift() != 0].sum(axis=1)
                        / data.shift()[data != 0].sum(axis=1),
                        axis=0,
                    )
                )
                .abs()
                .sum(axis=1, min_count=1)
            )
        else:
            diff = (
                (
                    data
                    - data.shift().multiply(
                        data.sum(axis=1) / data.shift().sum(axis=1),
                        axis=0,
                    )
                )
                .abs()
                .sum(axis=1, min_count=1)
            )

        # build result
        result = pd.Series(
            diff / (data.sum(axis=1, min_count=1) * 2),
            name="distribution",
        )

        # and maybe flatten
        if isinstance(self, Flatten):
            result = result.reindex_like(self._obj, method="ffill")

        return result

    def diff_skills(self, skip_na=True, skip_zero=True):

        """
        Calculate the difference in skills distribution from week to week in
        from a resampled DataFrame.

        Parameters
        ----------
        self : GroupBy or Resampling object

        Returns
        -------
        Series

        Example
        -------
        index = pd.date_range(start='2022-03-07 00:00:00', periods=21)
        data = {'skill 1': [20,20,10,15,10,10,10,
                            20,20,10,10,10,10,10,
                            20,20,10,10,10,10,10,],
                'skill 2': [20,10,20,5,10,10,10,
                            20,20,10,10,10,10,10,
                            20,10,20,10,10,10,10,],
                }
        frame = pd.DataFrame(index=index, data=data)

        >>> frame.blue.resample(rule=7).diff_skills()

        2022-03-07         NaN
        2022-03-14    0.027778
        2022-03-21    0.000000
        Name: skills, dtype: float64
        """

        # only works with resample('1w') or equivalent
        if self.rule != datetime.timedelta(days=7):
            raise ValueError(
                f"The object must be resampled to weekly data not {self.rule}"
            )

        # if the object is a Series return Series of zeros.
        if isinstance(self._obj, pd.Series):
            return pd.Series(
                index=self.grouped.sum().index,
                data=np.zeros(self.grouped.sum().size),
                name="skills",
            )

        # resample the data and transpose into a DataFrame with weekdays as columns
        data = self.grouped.apply(
            lambda x: pd.DataFrame(
                index=x.index.isocalendar().day,
                data=x.values,
                columns=x.columns,
            ).transpose()
        )

        # build a filter for the dataframe for weekdays with value zero or np.nan
        summed = data.groupby(level=0).apply(pd.DataFrame.sum, skipna=True)

        filt_index = pd.MultiIndex.from_product([summed.index, self._obj.columns])
        filt_data = np.repeat(summed.values, repeats=self._obj.shape[1], axis=0)

        if skip_na and skip_zero:
            filt_data = (filt_data != 0) & (np.logical_not(np.isnan(filt_data)))
        elif skip_na:
            filt_data = np.logical_not(np.isnan(filt_data))
        elif skip_zero:
            filt_data = filt_data != 0
        else:
            filt_data = np.full(filt_data.shape, True)

        filt = pd.DataFrame(
            index=filt_index,
            data=filt_data,
            columns=summed.columns,
        )

        # get diff_quantity to calculate the relative difference
        if skip_na and skip_zero:
            diff_quantity = summed[
                (summed.shift().notna()) & (summed.shift() != 0)
            ].sum(axis=1) / summed.shift()[(summed.notna()) & (summed != 0)].sum(axis=1)
        elif skip_na:
            diff_quantity = summed[summed.shift().notna()].sum(axis=1) / summed.shift()[
                summed.notna()
            ].sum(axis=1)
        elif skip_zero:
            diff_quantity = summed[summed.shift() != 0].sum(axis=1) / summed.shift()[
                summed != 0
            ].sum(axis=1)
        else:
            diff_quantity = summed.sum(axis=1) / summed.shift().sum(axis=1)

        # calculate diff_skills

        # filter the data with shifted filter and the shifted data with the unshifted filter
        # remember that the shift is equal to the number of skills (self._obj.shape[1])
        # sum the data for the weekdays
        # unstack the skills => the result is grouped data with skills as columns

        diff = (
            # the data with shifted filter minus the shifted data with filter
            (
                data[filt.shift(self._obj.shape[1])].sum(axis=1).unstack(level=1)
                - data.shift(self._obj.shape[1])[filt]
                .sum(axis=1)
                .unstack(level=1)
                .multiply(diff_quantity, axis=0)
            )
            .abs()
            .sum(axis=1, min_count=1)
        )

        # get the difference relative to the sum of the row with the shifted filter applied
        result = pd.Series(
            diff
            / (
                data[filt.shift(self._obj.shape[1])]
                .sum(axis=1)
                .unstack(level=1)
                .sum(axis=1, min_count=1)
                * 2
            ),
            name="skills",
        )

        if isinstance(self, Flatten):
            result = result.reindex_like(self._obj, method="ffill")
        return result

    setattr(cls, "sum", sum)
    setattr(cls, "mean", mean)
    setattr(cls, "var", var)
    setattr(cls, "std", std)
    setattr(cls, "min", min)
    setattr(cls, "max", max)
    setattr(cls, "count", count)
    setattr(cls, "value_range", value_range)
    setattr(cls, "subseries", subseries)
    setattr(cls, "diff_quantity", diff_quantity)
    setattr(cls, "diff_distribution", diff_distribution)
    setattr(cls, "diff_skills", diff_skills)
    return cls


@resolution_methods
class Resample:
    def __init__(self, _obj, rule, **kwargs):
        self._obj = _obj
        self.rule = _get_rule(rule)
        self.origin = _get_origin(_obj, self.rule)
        self.kwargs = kwargs
        self.calculate()

    def calculate(self, **kwargs):
        self.grouped = self._obj.resample(
            rule=self.rule, origin=self.origin, **self.kwargs
        )

    def __repr__(self):
        return self.grouped.__repr__()


@resolution_methods
class Flatten:
    """
    It is just a copy of Resample
    """

    def __init__(self, _obj, rule, **kwargs):
        self._obj = _obj
        self.rule = _get_rule(rule)
        self.origin = _get_origin(_obj, self.rule)
        self.kwargs = kwargs
        self.calculate()

    def calculate(self, **kwargs):
        self.grouped = self._obj.resample(
            rule=self.rule, origin=self.origin, **self.kwargs
        )

    def __repr__(self):
        return self.grouped.__repr__()


def _get_origin(_obj, rule):
    if (rule / datetime.timedelta(days=7)).is_integer():
        days = int(
            ((_obj.index.isocalendar().week[0] - 1) * 7) + _obj.index[0].weekday()
        )
        return _obj.index[0] - datetime.timedelta(days=days)
    elif (rule / datetime.timedelta(days=1)).is_integer():
        days = int(_obj.index[0].weekday())
        return _obj.index[0] - datetime.timedelta(days=days)
    else:
        return "start_day"


def _get_rule(rule):
    if isinstance(rule, str):
        rule = rule.replace(" ", "").lower()
        unit = rule.lstrip("0123456789")
        count = int(rule[0 : len(rule) - len(unit)]) if len(rule) > len(unit) else 1
        if unit in {"μs", "microsecond", "microseconds"}:
            return datetime.timedelta(microseconds=count)
        if unit in {"ms", "millisecond", "milliseconds"}:
            return datetime.timedelta(milliseconds=count)
        if unit in {"s", "sec", "second", "seconds"}:
            return datetime.timedelta(seconds=count)
        if unit in {"m", "min", "minute", "minutes"}:
            return datetime.timedelta(minutes=count)
        if unit in {"h", "hr", "hrs", "hour", "hours"}:
            return datetime.timedelta(hours=count)
        if unit in {"d", "day", "days"}:
            return datetime.timedelta(days=count)
        if unit in {"w", "wk", "week", "weeks"}:
            return datetime.timedelta(weeks=count)
    elif isinstance(rule, int):
        return datetime.timedelta(days=rule)
    else:
        return rule
