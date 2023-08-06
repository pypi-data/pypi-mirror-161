import numpy as np
import pandas as pd
import copy

import bluebelt.data.resolution
import bluebelt.data.projection

import bluebelt.analysis.datetime
import bluebelt.analysis.planning
import bluebelt.analysis.pattern
import bluebelt.analysis.performance

import bluebelt.statistics.std
import bluebelt.statistics.hypothesis_testing

import bluebelt.helpers.check as check

import bluebelt.helpers.holidays

import bluebelt.graph.graph

import datetime


@pd.api.extensions.register_series_accessor("_")
@pd.api.extensions.register_series_accessor("blue")
class SeriesToolkit:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        # self.index = self.index(self._obj)
        # self.statistics = self.statistics(self._obj)
        self.pattern = self.pattern(self._obj)
        self.planning = self.planning(self._obj)
        self.forecast = self.forecast(self._obj)
        # self.datetime = self.datetime(self._obj)
        # self.data = self.data(self._obj)
        # self.graph = self.graph(self._obj)
        self.stats = self.stats(self._obj)
        self.performance = self.performance(self._obj)

    def weekend(
        self, drop=False, fill_value=np.nan, inplace=False, weekend_days=[5, 6]
    ):
        """
        Fill all non-weekend data with the fill_value. If fill_value=None the
        Series or DataFrame will contain only the weekend days.

        The Series or DataFrame must have a DatetimeIndex

        Parameters
        ----------
        self : Series or DataFrame
        fill_value: object or None, default numpy.nan
        inplace: boolean, default False
        weekend_days: list of int, default [5, 6]

        Returns
        -------
        Series or DataFrame
        """
        # checks
        check.has_datetimeindex(self._obj)
        series = copy.deepcopy(self._obj) if not inplace else self._obj

        if fill_value is not None and not drop:
            series.loc[~series.index.weekday.isin(weekend_days)] = fill_value
        else:
            series = series[series.index.weekday.isin(weekend_days)]

        if inplace:
            return
        else:
            return series

    def not_weekend(
        self, drop=False, fill_value=np.nan, inplace=False, weekend_days=[5, 6]
    ):
        """
        Fill all weekend data with the fill_value. If fill_value=None the
        Series or DataFrame will contain only the non-weekend days.

        The Series or DataFrame must have a DatetimeIndex

        Parameters
        ----------
        self : Series or DataFrame
        fill_value: object or None, default numpy.nan
        inplace: boolean, default False
        weekend_days: list of int, default [5, 6]

        Returns
        -------
        Series or DataFrame
        """

        # checks
        check.has_datetimeindex(self._obj)
        series = copy.deepcopy(self._obj) if not inplace else self._obj

        if fill_value is not None and not drop:
            series.loc[series.index.weekday.isin(weekend_days)] = fill_value
        else:
            series = series[~series.index.weekday.isin(weekend_days)]

        if inplace:
            return
        else:
            return series

    weekdays = not_weekend

    def holiday(self, skip=None, drop=False, fill_value=np.nan, inplace=False):
        """
        Fill all non-holiday data with the fill_value. If fill_value=None the
        Series or DataFrame will contain only the holiday days.

        The Series or DataFrame must have a DatetimeIndex

        Parameters
        ----------
        self : Series or DataFrame
        fill_value: object or None, default numpy.nan
        inplace: boolean, default False

        Returns
        -------
        Series or DataFrame
        """

        # checks
        check.has_datetimeindex(self._obj)
        series = copy.deepcopy(self._obj) if not inplace else self._obj
        holidays = bluebelt.helpers.holidays.get_holidays(
            series.index.year.unique().to_list(), skip=skip
        )

        if fill_value is not None and not drop:
            series.loc[~series.index.isin(holidays)] = fill_value
        else:
            series = series[series.index.isin(holidays)]

        if inplace:
            return
        else:
            return series

    holidays = holiday

    def not_holiday(self, skip=None, drop=False, fill_value=np.nan, inplace=False):
        """
        Fill all holiday data with the fill_value. If fill_value=None the
        Series or DataFrame will contain only the non-holiday days.

        The Series or DataFrame must have a DatetimeIndex

        Parameters
        ----------
        self : Series or DataFrame
        fill_value: object or None, default numpy.nan
        inplace: boolean, default False

        Returns
        -------
        Series or DataFrame
        """

        # checks
        check.has_datetimeindex(self._obj)
        series = copy.deepcopy(self._obj) if not inplace else self._obj
        holidays = bluebelt.helpers.holidays.get_holidays(
            series.index.year.unique().to_list(), skip=skip
        )

        if fill_value is not None and not drop:
            series.loc[series.index.isin(holidays)] = fill_value
        else:
            series = series[~series.index.isin(holidays)]

        if inplace:
            return
        else:
            return series

    not_holidays = not_holiday

    def workdays(
        self, drop=False, fill_value=np.nan, inplace=False, weekend_days=[5, 6]
    ):
        """
        Fill all holiday and weekend data with the fill_value. If fill_value=None
        the Series or DataFrame will contain only the working days.

        The Series or DataFrame must have a DatetimeIndex

        Parameters
        ----------
        self : Series or DataFrame
        fill_value: object or None, default numpy.nan
        inplace: boolean, default False
        weekend_days: list of int, default [5, 6]

        Returns
        -------
        Series or DataFrame
        """

        # checks
        check.has_datetimeindex(self._obj)
        series = copy.deepcopy(self._obj) if not inplace else self._obj
        holidays = bluebelt.helpers.holidays.get_holidays(
            series.index.year.unique().to_list()
        )

        if fill_value is not None and not drop:
            series.loc[series.index.weekday.isin(weekend_days)] = fill_value
            series.loc[series.index.isin(holidays)] = fill_value
        else:
            series = series[~series.index.weekday.isin(weekend_days)]
            series = series[~series.index.isin(holidays)]

        if inplace:
            return
        else:
            return series

    def fill_na(self):
        """
        Fill all missing values of a pandas Series with the
        interpolated values of the previous and next weeks weekday.

        Parameters
        ----------
        self: Series

        Returns
        -------
        pandas.Series
        """
        # transform the dataframe
        rule = datetime.timedelta(weeks=1)
        origin = bluebelt.data.resolution._get_origin(self._obj, rule)

        data = self._obj.resample(rule=rule, origin=origin)
        data = data.apply(
            lambda x: pd.DataFrame(
                index=x.index.isocalendar().day,
                data=x.values,
            ).transpose()
        )
        data = data.droplevel(-1)

        # interpolate
        result = pd.DataFrame(index=data.index)
        for column in data:
            series = data[column]
            mask = np.isnan(series)
            series[mask] = np.interp(
                np.flatnonzero(mask), np.flatnonzero(~mask), series[~mask]
            )
            result[column] = series

        # finish
        result = result.stack()
        result = pd.Series(
            index=self._obj.index,
            data=result.values,
            name=self._obj.name,
        )

        return result

    def resample(self, rule="w", **kwargs):
        """
        Resample time-series data.
        The object must have a DatetimeIndex

        Parameters
        ----------
        self: Series or DataFrame
        rule: DateOffset, Timedelta or str, default 'week'
            The offset string or object representing target conversion.
            e.g. '1w', 'week', '4d', '4 days'
        kwargs: other pandas.Series.resample keywords

        Returns
        -------
        pandas.core.Resampler

        Methods
        -------
        sum: Calculate the sum of all the values in each group.
        mean: Calculate the mean of all the values in each group.
        var: Calculate the variance of all the values in each group.
        std: Calculate the standard deviation of all the values in each group.
        min: Calculate the minimum value of all the values in each group.
        max: Calculate the maximum value of all the values in each group.
        count: Calculate the count of all the values in each group.
        value_range: Calculate the value range of all the values in each group.
        subsize: Calculate the count of subgroups with a size that fit in each
            group.
        diff_quantity: Calculate the difference of the sum of all values
            in adjecent groups of the resampled DataFrame.
        diff_distribution: Calculate the difference in weekday distribution
            from week to week in from a resampled DataFrame. The rule for
            resampling must be '1w' or equivalent
        diff_skills: Calculate the difference in skills distribution from week
            to week in from a resampled DataFrame. The rule for resampling must
            be '1w' or equivalent.

        """
        check.has_datetimeindex(self._obj)
        return bluebelt.data.resolution.Resample(self._obj, rule, **kwargs)

    def flatten(self, rule="w", **kwargs):
        """
        Flatten time-series data.
        The object must have a DatetimeIndex

        Parameters
        ----------
        self: Series or DataFrame
        rule: DateOffset, Timedelta or str, default 'week'
            The offset string or object representing target conversion.
            e.g. '1w', 'week', '4d', '4 days'
        kwargs: other pandas.Series.resample keywords

        Returns
        -------
        Series

        """
        check.has_datetimeindex(self._obj)
        return bluebelt.data.resolution.Flatten(self._obj, rule, **kwargs)

    def project(self, year=None, adjust_holidays=True):
        return bluebelt.data.projection.project(
            self._obj, year=year, adjust_holidays=adjust_holidays
        )

    class pattern:
        def __init__(self, pandas_obj):
            self._obj = pandas_obj

        def polynomial(
            self,
            shape=(0, 6),
            validation="rsq",
            threshold=0.05,
            confidence=0.8,
            outlier_sigma=2,
            adjust=True,
            split=False,
        ):

            """
            Find the polynomial of an object.

            Parameters
            ----------
            series: pandas.Series
            shape: int or tuple, default (0, 6)
                when an int is provided the polynomial is provided as n-th degree polynomial
                when a tuple is provided the function will find an optimised polynomial between first and second value of the tuple
            validation: string, default p_val
                validation type for shape tuple
                p_val: test for normal distribution of the residuals
                rsq: check for improvement of the rsq value
            threshold: float, default 0.05
                the threshold for normal distribution test or rsq improvement
            confidence: float, default 0.8
                the bound confidence
            outlier_sigma: float, default 2
                outliers are datapoints outside the outlier_sigma fraction
            adjust: boolean, default True
                adjust polynomial for outliers
            split: boolean, default False
                split the data into years

            Returns
            -------
            Polynomial

            Performance Methods
            -------------------
            Additional methods to evaluate the process performance.

            Provide the values parameter to choose for which values the
            performance should be evaluated

            summary(values=None)
            control_chart(values=None)
            run_chart(values=None)
            process_capability(values=None)
            """
            if split:
                return bluebelt.analysis.pattern.FramePolynomial(
                    pd.Series(
                        index=pd.MultiIndex.from_frame(self._obj.index.isocalendar()),
                        data=self._obj.values,
                    ).unstack(level=0),
                    shape=shape,
                    validation=validation,
                    threshold=threshold,
                    confidence=confidence,
                    outlier_sigma=outlier_sigma,
                    adjust=adjust,
                )
            else:
                return bluebelt.analysis.pattern.Polynomial(
                    self._obj,
                    shape=shape,
                    validation=validation,
                    threshold=threshold,
                    confidence=confidence,
                    outlier_sigma=outlier_sigma,
                    adjust=adjust,
                )

        def periodical(
            self,
            rule="1W",
            how="mean",
            confidence=0.8,
            outlier_sigma=2,
            adjust=True,
            **kwargs,
        ):

            """
            Find the periodical of an object.

            Parameters
            ----------
            series: pandas.Series
            rule: str, default "1W"
                period representation used for resampling the series
            how: str, default "mean"
                define how the period must be evaluated
                options are "mean", "min", "max" and "std"
            confidence: float, default 0.8
                the bandwidth confidence
            outlier_sigma: float, default 2
                outliers are datapoints outside the outlier_sigma fraction

            Returns
            -------
            Periodical

            Performance Methods
            -------------------
            Additional methods to evaluate the process performance.

            Provide the values parameter to choose for which values the
            performance should be evaluated

            summary(values=None)
            control_chart(values=None)
            run_chart(values=None)
            process_capability(values=None)
            """
            return bluebelt.analysis.pattern.Periodical(
                self._obj,
                rule=rule,
                how=how,
                confidence=confidence,
                outlier_sigma=outlier_sigma,
                adjust=adjust,
                **kwargs,
            )

        def week_day(self, **kwargs):
            """
            Compare the distribution of data between week days

            Parameters
            ----------
            self : Series

            Returns
            -------
            WeekDay

            Attributes
            ----------
            series
                the transformed pandas.Series
            data
                the data
            equal_means
                the result of bluebelt.statistics.hypothesis_testing.EqualMeans().passed
            equal_variances
                the result of bluebelt.statistics.hypothesis_testing.EqualVariances().passed

            Methods
            -------
            plot: return the WeekDay plot
            """

            return bluebelt.analysis.datetime.WeekDay(self._obj, **kwargs)

        weekday = week_day

        def month_day(self, **kwargs):
            """
            Compare the distribution of data between month days

            Parameters
            ----------
            self : Series

            Returns
            -------
            MonthDay

            Attributes
            ----------
            series
                the transformed pandas.Series
            data
                the data
            equal_means
                the result of bluebelt.statistics.hypothesis_testing.EqualMeans().passed
            equal_variances
                the result of bluebelt.statistics.hypothesis_testing.EqualVariances().passed

            Methods
            -------
            plot: return the MonthDay plot
            """
            return bluebelt.analysis.datetime.MonthDay(self._obj, **kwargs)

        day = month_day

        def week(self, **kwargs):
            """
            Compare the distribution of data between weeks

            Parameters
            ----------
            self : Series

            Returns
            -------
            Week

            Attributes
            ----------
            series
                the transformed pandas.Series
            data
                the data
            equal_means
                the result of bluebelt.statistics.hypothesis_testing.EqualMeans().passed
            equal_variances
                the result of bluebelt.statistics.hypothesis_testing.EqualVariances().passed

            Methods
            -------
            plot: return the Week plot
            """
            return bluebelt.analysis.datetime.Week(self._obj, **kwargs)

        def month(self, **kwargs):
            """
            Compare the distribution of data between months

            Parameters
            ----------
            self : Series

            Returns
            -------
            Month

            Attributes
            ----------
            series
                the transformed pandas.Series
            data
                the data
            equal_means
                the result of bluebelt.statistics.hypothesis_testing.EqualMeans().passed
            equal_variances
                the result of bluebelt.statistics.hypothesis_testing.EqualVariances().passed

            Methods
            -------
            plot: return the Month plot
            """
            return bluebelt.analysis.datetime.Month(self._obj, **kwargs)

        def year(self, **kwargs):
            """
            Compare the distribution of data between years

            Parameters
            ----------
            self : Series

            Returns
            -------
            Year

            Attributes
            ----------
            series
                the transformed pandas.Series
            data
                the data
            equal_means
                the result of bluebelt.statistics.hypothesis_testing.EqualMeans().passed
            equal_variances
                the result of bluebelt.statistics.hypothesis_testing.EqualVariances().passed

            Methods
            -------
            plot: return the Year plot
            """
            return bluebelt.analysis.datetime.Year(self._obj, **kwargs)

    patterns = pattern

    class planning:
        def __init__(self, pandas_obj):
            self._obj = pandas_obj

        def effort(self, skip_na=True, skip_zero=True):
            """
            Get the planning effort metrics.

            Parameters
            ----------
            self: Series or DataFrame

            Returns
            -------
            bluebelt.Effort

            Methods
            -------
            plot: return the WeekDay plot

            Performance Methods
            -------------------
            Additional methods to evaluate the process performance.

            Provide the values parameter to choose for which values the
            performance should be evaluated

            summary(values=None)
            control_chart(values=None)
            run_chart(values=None)
            process_capability(values=None)
            """
            return bluebelt.analysis.planning.Effort(
                self._obj, skip_na=skip_na, skip_zero=skip_zero
            )

        def ease(self, **kwargs):
            """
            Get the planning ease metrics.

            Parameters
            ----------
            self: Series or DataFrame

            Returns
            -------
            bluebelt.Ease

            Methods
            -------
            plot: return an ease plot

            Performance Methods
            -------------------
            Additional methods to evaluate the process performance.

            Provide the values parameter to choose for which values the
            performance should be evaluated

            summary(values=None)
            control_chart(values=None)
            run_chart(values=None)
            process_capability(values=None)
            """
            return bluebelt.analysis.planning.Ease(self._obj, **kwargs)

    class stats:
        def __init__(self, pandas_obj):
            self._obj = pandas_obj

        def index(self):
            return bluebelt.statistics.hypothesis_testing.index()

        # hypothesis testing
        def dagostino_pearson(self, alpha=0.05, **kwargs):
            return bluebelt.statistics.hypothesis_testing.DAgostinoPearson(
                self._obj, alpha=alpha
            )

        normal_distribution = dagostino_pearson

        def anderson_darling(self, dist="norm", alpha=0.05, **kwargs):
            return bluebelt.statistics.hypothesis_testing.AndersonDarling(
                self._obj, dist=dist, alpha=alpha
            )

        def std_within(self, how=None, observations=2, **kwargs):
            return bluebelt.statistics.std.StdWithin(
                self._obj, how=how, observations=observations, **kwargs
            )

        def one_sample_t(self, popmean=None, alpha=0.05, **kwargs):
            return bluebelt.statistics.hypothesis_testing.OneSampleT(
                self._obj, popmean=popmean, alpha=alpha, **kwargs
            )

        def wilcoxon(self, alpha=0.05, **kwargs):
            return bluebelt.statistics.hypothesis_testing.Wilcoxon(
                self._obj, alpha=alpha, **kwargs
            )

    class performance:
        def __init__(self, pandas_obj):
            self._obj = pandas_obj

        def summary(self, **kwargs):
            return bluebelt.analysis.performance.Summary(self._obj, **kwargs)

        def control_chart(self, **kwargs):
            """
            Calculate and display a control chart.

            Parameters
            ----------
            self : Series
            format_stats: str, default "1.2f"
                the formatting for all statistics returned

            Returns
            -------
            ControlChart

            Attributes
            ----------
            series
                the Series

            mean:
                float with the mean
            std:
                float with the standard deviation
            ucl:
                float with the upper control limit
            lcl:
                float with the lower control limit
            outliers:
                the outliers as a Series
            outlier_count:
                int with the number of outliers

            Methods
            -------
            plot:
                return the ControlChart plot

            """
            return bluebelt.analysis.performance.ControlChart(self._obj, **kwargs)

        def run_chart(self, **kwargs):
            """
            Calculate and display a run chart

            The number of runs about the median is the total number of runs above the median
            and the total number of runs below the median.
            A run about the median is one or more consecutive points on the same side of the
            center line.
            A run ends when the line that connects the points crosses the center line.
            A new run begins with the next plotted point.
            A data point equal to the median belongs to the run below the median.

            The number of runs up or down is the total count of upward and downward runs in
            the series.
            A run up or down ends when the direction changes.

            Clustering, mixtures, trends and oscillation
            A p-value that is less than the specified level of significance (alpha) indicates
            clustering, mixtures, trends and/or oscillation

            Parameters
            ----------
            self : Series
            alpha: float, default 0.05
                the threshold for clustering, mixtures, trends and oscillation
            format_stats: str, default "1.2f"
                the formatting for all statistics returned

            Returns
            -------
            RunChart

            Attributes
            ----------
            series
                the Series
            alpha:
            format_stats:
            metrics:
                prints the run chart metrics (all metrics below)
            runs_about:
                the number of runs about the median
            expected_runs_about:
                the expected number of runs about the median
            longest_run_about:
                the longest run about the median
            runs_up_or_down:
                the number of runs up or down
            expected_runs_up_or_down:
                the expected number of runs up or down
            longest_run_up_or_down:
                the longest run up or down
            p_value_clustering:
                the p-value for clustering
            p_value_mixtures:
                the p-value for mixtures
            p_value_trends:
                the p-value for trends
            p_value_oscillation:
                the p-value for oscillation
            clustering:
                boolean value for clustering
            mixtures:
                boolean value for mixtures
            trends:
                boolean value for trends
            oscillation:
                boolean value for oscillation
            longest_runs_about:
                a list of the longest run or runs about the median
            longest_runs_up_or_down:
                a list of the longest run or runs up or down

            Methods
            -------
            plot:
                return the RunChart plot

            """
            return bluebelt.analysis.performance.RunChart(self._obj, **kwargs)

        def process_capability(self, **kwargs):
            """
            Calculate and display the process capability

            Parameters
            ----------
            self : Series
            target: float, default None
                target value for the process
            usl: float, default None
                upper specification limit (usl and ub cannot be specified both)
            ub: float, default None
                upper bound (usl and ub cannot be specified both)
            lsl: float, default None
                lower specification limit
            lb: float, default None
                lower bound (lsl and lb cannot be specified both)
            tolerance: float, default 6.0
                sigma tolerance of the process


            alpha: float, default 0.05
                the threshold for clustering, mixtures, trends and oscillation
            format_stats: str, default "1.2f"
                the formatting for all statistics returned

            Returns
            -------
            RunChart

            Attributes
            ----------
            series
                the Series
            min
            max
            mean
            std
            std_within

            ### observed performance
            observed_lt_lsl
            observed_gt_usl
            observed_performance

            ### expected performance
            expected_lt_lsl_within
            expected_gt_usl_within
            expected_performance_within

            expected_lt_lsl_overall
            expected_gt_usl_overall
            expected_performance_overall

            ### within capability
            cp
            cpl
            cpu
            cpk
            ccpk

            ### overall capability
            pp
            ppl
            ppu
            ppk
            cpm

            Methods
            -------
            df
                show the process capability in a pandas.DataFrame
            plot
                return the ProcessCapability plot

            """
            return bluebelt.analysis.performance.ProcessCapability(self._obj, **kwargs)

    class forecast:
        def __init__(self, pandas_obj):
            self._obj = pandas_obj

        def MAE(self, **kwargs):
            """
            Find the Mean Absolute Error.

            Parameters
            ----------
            self: pandas.DataFrame
            forecast: str, default None
                the column name with the forecast data
                if forecast is None the first column of the DataFrame will be
                used as forecast data
            actuals: str, default None
                the column name with the actuals data
                if actuals is None the second column of the DataFrame will be
                used as actuals data

            Returns
            -------
            MAE

            Performance Methods
            -------------------
            Additional methods to evaluate the process performance.

            Provide the values parameter to choose for which values the
            performance should be evaluated

            summary(values=None)
            control_chart(values=None)
            run_chart(values=None)
            process_capability(values=None)

            """
            return bluebelt.analysis.forecast.MAE(self._obj, **kwargs)

        def MAPE(self, **kwargs):
            """
            Find the Mean Absolute Percentage Error.

            Parameters
            ----------
            self: pandas.DataFrame
            forecast: str, default None
                the column name with the forecast data
                if forecast is None the first column of the DataFrame will be
                used as forecast data
            actuals: str, default None
                the column name with the actuals data
                if actuals is None the second column of the DataFrame will be
                used as actuals data

            Returns
            -------
            MAPE

            Performance Methods
            -------------------
            Additional methods to evaluate the process performance.

            Provide the values parameter to choose for which values the
            performance should be evaluated

            summary(values=None)
            control_chart(values=None)
            run_chart(values=None)
            process_capability(values=None)

            """
            return bluebelt.analysis.forecast.MAPE(self._obj, **kwargs)

        def SMAPE(self, **kwargs):
            """
            Find the Symmetrical Mean Absolute Percentage Error.

            Parameters
            ----------
            self: pandas.DataFrame
            forecast: str, default None
                the column name with the forecast data
                if forecast is None the first column of the DataFrame will be
                used as forecast data
            actuals: str, default None
                the column name with the actuals data
                if actuals is None the second column of the DataFrame will be
                used as actuals data
            adjust: boolean, default True
                calculate use the adjusted SMAPE

            Returns
            -------
            SMAPE

            Performance Methods
            -------------------
            Additional methods to evaluate the process performance.

            Provide the values parameter to choose for which values the
            performance should be evaluated

            summary(values=None)
            control_chart(values=None)
            run_chart(values=None)
            process_capability(values=None)

            """
            return bluebelt.analysis.forecast.SMAPE(self._obj, **kwargs)

        def MDA(self, **kwargs):
            """
            Find the Mean Directional Accuracy.

            Parameters
            ----------
            self: pandas.DataFrame
            forecast: str, default None
                the column name with the forecast data
                if forecast is None the first column of the DataFrame will be
                used as forecast data
            actuals: str, default None
                the column name with the actuals data
                if actuals is None the second column of the DataFrame will be
                used as actuals data

            Returns
            -------
            MDA
            """
            return bluebelt.analysis.forecast.MDA(self._obj, **kwargs)

        def MPE(self, **kwargs):
            """
            Find the Mean Percentage Error.

            Parameters
            ----------
            self: pandas.DataFrame
            forecast: str, default None
                the column name with the forecast data
                if forecast is None the first column of the DataFrame will be
                used as forecast data
            actuals: str, default None
                the column name with the actuals data
                if actuals is None the second column of the DataFrame will be
                used as actuals data
            confidence: float, default 0.95
                the confidence for measuring the confidence interval of the mean

            Returns
            -------
            MPE

            Performance Methods
            -------------------
            Additional methods to evaluate the process performance.

            Provide the values parameter to choose for which values the
            performance should be evaluated

            summary(values=None)
            control_chart(values=None)
            run_chart(values=None)
            process_capability(values=None)

            """
            return bluebelt.analysis.forecast.MPE(self._obj, **kwargs)

        def NFM(self, **kwargs):
            """
            Find the Normalized Forecast Metric. If the result > 0 the forecast
            tends to be greater than the actuals.

            Parameters
            ----------
            self: pandas.DataFrame
            forecast: str, default None
                the column name with the forecast data
                if forecast is None the first column of the DataFrame will be
                used as forecast data
            actuals: str, default None
                the column name with the actuals data
                if actuals is None the second column of the DataFrame will be
                used as actuals data
            confidence: float, default 0.95
                the confidence for measuring the confidence interval of the mean

            Returns
            -------
            NFM

            """
            return bluebelt.analysis.forecast.NFM(self._obj, **kwargs)

        mae = MAE
        mape = MAPE
        smape = SMAPE
        mda = MDA
        mpe = MPE
        nfm = NFM
        bias = NFM

    def line(
        self,
        xlim=(None, None),
        ylim=(None, None),
        max_xticks=None,
        format_xticks=None,
        format_yticks=None,
        title=None,
        xlabel=None,
        ylabel=None,
        legend=True,
        path=None,
        **kwargs,
    ):
        return bluebelt.graph.graph.line(
            self._obj,
            xlim=xlim,
            ylim=ylim,
            max_xticks=max_xticks,
            format_xticks=format_xticks,
            format_yticks=format_yticks,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            legend=legend,
            path=path,
            **kwargs,
        )

    def area(
        self,
        xlim=(None, None),
        ylim=(None, None),
        max_xticks=None,
        format_xticks=None,
        format_yticks=None,
        title=None,
        xlabel=None,
        ylabel=None,
        legend=True,
        path=None,
        **kwargs,
    ):
        return bluebelt.graph.graph.area(
            self._obj,
            xlim=xlim,
            ylim=ylim,
            max_xticks=max_xticks,
            format_xticks=format_xticks,
            format_yticks=format_yticks,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            legend=legend,
            path=path,
            **kwargs,
        )

    def hist(
        self,
        bins=20,
        xlim=(None, None),
        ylim=(None, None),
        format_xticks=None,
        format_yticks=None,
        title=None,
        xlabel=None,
        ylabel=None,
        legend=True,
        path=None,
        **kwargs,
    ):
        return bluebelt.graph.graph.hist(
            self._obj,
            bins=bins,
            xlim=xlim,
            ylim=ylim,
            format_xticks=format_xticks,
            format_yticks=format_yticks,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            legend=legend,
            path=path,
            **kwargs,
        )

    histogram = hist

    def box(
        self,
        xlim=(None, None),
        ylim=(None, None),
        format_xticks=None,
        format_yticks=None,
        title=None,
        xlabel=None,
        ylabel=None,
        path=None,
        **kwargs,
    ):
        return bluebelt.graph.graph.box(
            self._obj,
            xlim=xlim,
            ylim=ylim,
            format_xticks=format_xticks,
            format_yticks=format_yticks,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            path=path,
            **kwargs,
        )

    boxplot = box

    def waterfall(
        self,
        horizontal=False,
        swapx=False,
        swapy=False,
        width=0.6,
        height=0.6,
        xlim=(None, None),
        ylim=(None, None),
        format_xticks=None,
        format_yticks=None,
        title=None,
        xlabel=None,
        ylabel=None,
        path=None,
        **kwargs,
    ):
        return bluebelt.graph.graph.waterfall(
            self._obj,
            horizontal=horizontal,
            swapx=swapx,
            swapy=swapy,
            width=width,
            height=height,
            xlim=xlim,
            ylim=ylim,
            format_xticks=format_xticks,
            format_yticks=format_yticks,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            path=path,
            **kwargs,
        )
