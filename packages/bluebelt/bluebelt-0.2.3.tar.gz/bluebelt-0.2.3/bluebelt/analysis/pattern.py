import os
import pandas as pd
import numpy as np
import scipy.stats as stats
import datetime
import warnings

import matplotlib.pyplot as plt
import matplotlib.dates


from bluebelt.helpers.date import year_with_most_iso_weeks
import bluebelt.helpers.ticks

from bluebelt.helpers.decorators.performance import performance
from bluebelt.helpers.decorators.pattern import pattern


@pattern
@performance
class Polynomial:
    def __init__(
        self,
        _obj,
        shape=(0, 6),
        validation="rsq",
        threshold=0.05,
        confidence=0.8,
        outlier_sigma=2,
        adjust=True,
        **kwargs,
    ):

        self._obj = _obj
        self.name = _obj.name or "obj"
        self.shape = shape
        self.validation = validation
        self.threshold = threshold
        self.confidence = confidence
        self.outlier_sigma = outlier_sigma
        self.adjust = adjust

        self.calculate()

    def calculate(self):

        # set pattern and residuals
        _poly_hand_granade(self)

        # set outliers
        _set_outliers(self)

        # handle adjusted
        self.adjusted = self._obj.loc[~self.outliers.notnull()]
        if self.adjust:

            self.__obj = self._obj.copy()  # backup

            # replace outliers with None values so they will be ignored by _poly_hand_granade and reset pattern
            self._obj = pd.Series(
                data=np.where(self.outliers.notnull(), None, self._obj).astype(
                    np.float
                ),
                index=self._obj.index,
            )
            _poly_hand_granade(self)

            self._obj = self.__obj.copy()  # and reset
            del self.__obj

        # handle bounds
        _set_bounds(self)

        # set final shape
        if hasattr(self, "_shape"):
            self.shape = self._shape
            del self._shape

    def set_observations(self):
        _set_observations(self)

    def set_residuals(self):
        _set_residuals(self)

    def set_outliers(self):
        _set_outliers(self)

    def set_bounds(self):
        _set_bounds(self)

    def __repr__(self):
        return f"{self.__class__.__name__}(n={self._obj.size:1.0f}, shape={self.shape}, validation='{self.validation}', threshold={self.threshold}, confidence={self.confidence}, outlier_sigma={self.outlier_sigma}, adjust={self.adjust}, outliers={self.outliers_count}, rsq={self.rsq:1.2f}, std={self.std:1.2f}, p_value={self.p_value:1.2f})"

    def __str__(self):
        _result = f"-" * (len(self.name) + 4) + "\n"
        _result += f"  {self.name}\n"
        _result += f"-" * (len(self.name) + 4) + "\n"
        _result += f"\n"

        _result += f"input variables\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"_obj size:":<30}{self._obj.size:1.0f}\n'
        _result += f'  {"validation type:":<30}{self.validation}\n'
        _result += f'  {"validation threshold:":<30}{self.threshold:1.4f}\n'

        _result += f"\n"
        _result += f"pattern\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"shape:":<30}{self.shape:1.0f}\n'
        _result += f'  {"r squared:":<30}{self.rsq:1.2f}\n'

        _result += f"\n"
        _result += f"residuals\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"bounds level:":<30}{self.confidence * 100:1.0f}%\n'
        _result += f'  {"bounds size:":<30}{self.bounds * 2:1.2f}\n'
        _result += f'  {"standard deviation:":<30}{self.std:1.2f}\n'
        _result += f'  {"p-value normal distribution:":<30}{self.p_value:1.4f}\n'
        _result += f'  {"outliers:":<30}{self.outliers_count:1.0f}\n'

        return _result

    def plot(
        self,
        bounds=True,
        residuals=False,
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
        return _plot(
            self,
            bounds=bounds,
            residuals=residuals,
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


class FramePolynomial:
    def __init__(
        self,
        _obj,
        shape=(0, 6),
        validation="rsq",
        threshold=0.05,
        confidence=0.8,
        outlier_sigma=2,
        adjust=True,
        **kwargs,
    ):

        self._obj = _obj
        self.shape = shape
        self.validation = validation
        self.threshold = threshold
        self.confidence = confidence
        self.outlier_sigma = outlier_sigma
        self.adjust = adjust

        # handle pandas MultiIndex from isocalendar
        if isinstance(_obj.index, pd.MultiIndex) and _obj.index.names == [
            "week",
            "day",
        ]:
            year = year_with_most_iso_weeks(_obj.columns)
            _index = np.apply_along_axis(
                lambda x: datetime.datetime.fromisocalendar(year, x[0], x[1]),
                1,
                np.array([*_obj.index.values]),
            )
        else:
            _index = _obj.index

        _pattern = pd.DataFrame(index=_index)
        _upper = pd.DataFrame(index=_index)
        _lower = pd.DataFrame(index=_index)

        for column in _obj.columns:

            series = pd.Series(index=_index, data=_obj[column].values, name=column)
            _poly = Polynomial(
                series,
                shape=shape,
                validation=validation,
                threshold=threshold,
                confidence=confidence,
                outlier_sigma=outlier_sigma,
                adjust=adjust,
                **kwargs,
            )

            _pattern[column] = _poly.pattern
            _upper[column] = _poly.upper
            _lower[column] = _poly.lower

        # dummy patterns with false datetime index to make plot easier
        self._pattern = _pattern
        self._upper = _upper
        self._lower = _lower

        self.pattern = pd.DataFrame(
            index=_obj.index, data=_pattern.values, columns=_pattern.columns
        )
        self.upper = pd.DataFrame(
            index=_obj.index, data=_upper.values, columns=_upper.columns
        )
        self.lower = pd.DataFrame(
            index=_obj.index, data=_lower.values, columns=_lower.columns
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(n={self._obj.size:1.0f}, shape={self.shape}, validation='{self.validation}', threshold={self.threshold}, confidence={self.confidence}, outlier_sigma={self.outlier_sigma}, adjust={self.adjust})"

    def plot(self, **kwargs):
        return _frame_plot(self, **kwargs)


@pattern
@performance
class Periodical:
    def __init__(
        self,
        _obj,
        rule="1W",
        how="mean",
        confidence=0.8,
        outlier_sigma=2,
        adjust=True,
        **kwargs,
    ):

        self._obj = _obj
        self.name = _obj.name or "obj"
        self.rule = rule
        self.how = how
        self.confidence = confidence
        self.outlier_sigma = outlier_sigma
        self.adjust = adjust

        self.calculate()

    def calculate(self):

        # set pattern and residuals
        _peri_hand_granade(self)

        # set outliers
        self.outliers = pd.Series(
            data=np.where(
                self.residuals.abs() > self.residuals.std() * self.outlier_sigma,
                self._obj,
                None,
            ),
            index=self._obj.index,
            name=f"{self._obj.name} {self.rule} outliers",
        )
        self.outliers_count = np.count_nonzero(self.outliers)

        # handle adjusted
        self.adjusted = self._obj.loc[~self.outliers.notnull()]
        if self.adjust:

            self.__obj = self._obj.copy()  # backup

            # replace outliers with None values so they will be ignored by _poly_hand_granade and reset pattern
            self._obj = pd.Series(
                data=np.where(self.outliers.notnull(), None, self._obj).astype(
                    np.float
                ),
                index=self._obj.index,
                name=self._obj.name,
            )
            _peri_hand_granade(self)

            self._obj = self.__obj.copy()  # and reset
            del self.__obj

        # handle bounds
        _set_bounds(self)

    def set_observations(self):
        _set_observations(self)

    def set_residuals(self):
        _set_residuals(self)

    def set_outliers(self):
        _set_outliers(self)

    def set_bounds(self):
        _set_bounds(self)

    def __repr__(self):
        return f"{self.__class__.__name__}(n={self._obj.size:1.0f}, rule={self.rule}, how={self.how}, confidence={self.confidence}, outlier_sigma={self.outlier_sigma}, adjust={self.adjust}, outliers={self.outliers_count})"

    def plot(
        self,
        bounds=True,
        residuals=False,
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
        return _plot(
            self,
            bounds=bounds,
            residuals=residuals,
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


def _poly_hand_granade(_poly):

    # get index and _index
    index = matplotlib.dates.date2num(
        _poly._obj.index
    )  # bluebelt.core.index.IndexToolkit(_poly._obj.index).clean()
    _index = matplotlib.dates.date2num(
        _poly._obj.dropna().index
    )  # bluebelt.core.index.IndexToolkit(_poly._obj.dropna().index).clean()

    # get the values
    _values = _poly._obj.dropna().values

    if isinstance(_poly.shape, int):
        polyfit = np.polynomial.polynomial.polyfit(_index, _values, _poly.shape)
        _poly.pattern = pd.Series(
            index=_poly._obj.index,
            data=np.polynomial.polynomial.polyval(index, polyfit),
            name=f"{_poly.name} {_get_nice_polynomial_name(_poly.shape)}",
        )
        _poly.residuals = (_poly._obj - _poly.pattern).rename(
            f"{_poly.name} {_get_nice_polynomial_name(_poly.shape)} residuals"
        )

        _poly.statistic, _poly.p_value = stats.normaltest(
            _poly.residuals.dropna().values
        )
        np_err = np.seterr(
            divide="ignore", invalid="ignore"
        )  # ignore possible divide by zero
        _poly.rsq = (
            np.corrcoef(
                _poly._obj.dropna().values, _poly.pattern[~_poly._obj.isna()].values
            )[1, 0]
            ** 2
        )
        np.seterr(**np_err)  # go back to previous settings
        _poly.std = _poly.residuals.std()

    elif isinstance(_poly.shape, tuple):

        _results = {}
        _validation = {}

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            for shape in range(_poly.shape[0], _poly.shape[1] + 1):
                try:
                    polyfit = np.polynomial.polynomial.polyfit(_index, _values, shape)
                    pattern = pd.Series(
                        index=_poly._obj.index,
                        data=np.polynomial.polynomial.polyval(index, polyfit),
                        name=f"{_poly.name} {_get_nice_polynomial_name(shape)}",
                    )
                    residuals = (_poly._obj - pattern).rename(
                        f"{_poly.name} {_get_nice_polynomial_name(shape)} residuals"
                    )

                    statistic, p_value = stats.normaltest(residuals.dropna().values)
                    np_err = np.seterr(
                        divide="ignore", invalid="ignore"
                    )  # ignore possible divide by zero
                    rsq = (
                        np.corrcoef(
                            _poly._obj.dropna().values,
                            pattern[~_poly._obj.isna()].values,
                        )[1, 0]
                        ** 2
                    )
                    np.seterr(**np_err)  # go back to previous settings
                    std = residuals.std()

                    _results[shape] = {
                        "pattern": pattern,
                        "residuals": residuals,
                        "statistic": statistic,
                    }
                    _validation[shape] = {
                        "p_value": p_value,
                        "rsq": rsq,
                        "std": std,
                    }

                except np.polynomial.polynomial.pu.RankWarning:
                    # print(f'RankWarning at {_get_nice_polynomial_name(shape)}')
                    pass  # break

        if _poly.validation == "p_value":
            validation = pd.DataFrame.from_dict(_validation).loc[_poly.validation]

            # if any p_value >= threshold then we have a winner
            if (validation >= _poly.threshold).any():
                shape = validation.idxmax()
            else:
                shape = 0

        elif _poly.validation == "std":

            # we want a small std of the residuals
            validation = pd.DataFrame.from_dict(_validation).loc[_poly.validation]

            # are there any relevant improvements?
            if (validation.diff().abs() / validation.shift() >= _poly.threshold).any():
                # find the relevant improvements
                relevant = validation.iloc[validation.diff().idxmin() :]

                # does it get any better than this?
                improvements = (
                    relevant.diff() / relevant.shift(1)
                ).abs() >= _poly.threshold
                improvements.at[validation.diff().idxmin()] = True  # because it must be

                # where does it stop getting better?
                first_fail = (
                    improvements.where(improvements == False).first_valid_index()
                    or improvements.index.max() + 1
                )

                # so what is the shape?
                shape = improvements[improvements.index < first_fail].index.max()
            else:
                shape = validation.index[0]

        else:  # the default
            _poly.validation = "rsq"

            # we want a big rsq value
            validation = pd.DataFrame.from_dict(_validation).loc[_poly.validation]

            # are there any relevant improvements?
            if (validation.diff().abs() / validation.shift() >= _poly.threshold).any():
                # find the relevant improvements
                relevant = validation.iloc[validation.diff().idxmax() :]

                # does it get any better than this?
                improvements = (
                    relevant.diff() / relevant.shift(1)
                ).abs() >= _poly.threshold
                improvements.at[validation.diff().idxmax()] = True  # because it must be

                # where does it stop getting better?
                first_fail = (
                    improvements.where(improvements == False).first_valid_index()
                    or improvements.index.max() + 1
                )

                # so what is the shape?
                shape = improvements[improvements.index < first_fail].index.max()
            else:
                shape = validation.index[0]

        _poly.pattern = _results.get(shape).get("pattern")
        _poly.residuals = _results.get(shape).get("residuals")
        _poly._shape = shape
        _poly.statistic = _results.get(shape).get("statistic")
        _poly.p_value = _validation.get(shape).get("p_value")
        _poly.rsq = _validation.get(shape).get("rsq")
        _poly.std = _validation.get(shape).get("std")

    else:
        _poly.pattern = None
        _poly.residuals = None

    return


def _peri_hand_granade(_peri, **kwargs):

    # set pattern and residuals
    if _peri.how == "mean":
        _peri.pattern = bluebelt.data.resolution.Flatten(
            _peri._obj, _peri.rule, **kwargs
        ).mean()
    elif _peri.how == "min":
        _peri.pattern = bluebelt.data.resolution.Flatten(
            _peri._obj, _peri.rule, **kwargs
        ).min()
    elif _peri.how == "max":
        _peri.pattern = bluebelt.data.resolution.Flatten(
            _peri._obj, _peri.rule, **kwargs
        ).max()
    elif _peri.how == "std":
        _peri.pattern = bluebelt.data.resolution.Flatten(
            _peri._obj, _peri.rule, **kwargs
        ).std()
    else:
        _peri.pattern = bluebelt.data.resolution.Flatten(
            _peri._obj, _peri.rule, **kwargs
        ).sum()

    _peri.residuals = _peri._obj - _peri.pattern

    _peri.statistic, _peri.p_value = stats.normaltest(_peri.residuals.dropna().values)
    _peri.rsq = np.corrcoef(_peri._obj.values, _peri.pattern.values)[1, 0] ** 2

    return


def _set_observations(_poly):
    _poly._obj = (_poly.pattern + _poly.residuals).rename(_poly._obj.name)


def _set_residuals(_poly):
    _poly.residuals = (_poly._obj - _poly.pattern).rename(f"residuals")

    _poly.statistic, _poly.p_value = stats.normaltest(_poly.residuals.dropna().values)
    np_err = np.seterr(
        divide="ignore", invalid="ignore"
    )  # ignore possible divide by zero
    _poly.rsq = (
        np.corrcoef(
            _poly._obj.dropna().values,
            _poly.pattern[~_poly._obj.isna()].values,
        )[1, 0]
        ** 2
    )
    np.seterr(**np_err)  # go back to previous settings
    _poly.std = _poly.residuals.std()


def _set_outliers(_poly):
    # set outliers
    _poly.outliers = pd.Series(
        data=np.where(
            _poly.residuals.abs() > _poly.residuals.std() * _poly.outlier_sigma,
            _poly._obj,
            None,
        ),
        index=_poly._obj.index,
    )
    _poly.outliers_count = np.count_nonzero(_poly.outliers)

    return _poly


def _set_bounds(_poly):

    _poly.sigma_level = stats.norm.ppf(1 - (1 - _poly.confidence) / 2)

    # set bounds
    _poly.upper = _poly.pattern + _poly.residuals.std() * _poly.sigma_level
    _poly.lower = _poly.pattern - _poly.residuals.std() * _poly.sigma_level
    _poly.bounds = _poly.residuals.std() * _poly.sigma_level

    # set out of bounds values
    _poly.out_of_bounds = _poly._obj.where(
        ((_poly._obj > _poly.upper) | (_poly._obj < _poly.lower))
        & (_poly.outliers.isnull()),
        np.nan,
    )
    _poly.within_bounds = _poly._obj.where(
        (_poly._obj <= _poly.upper) & (_poly._obj >= _poly.lower), np.nan
    )

    return _poly


def _get_nice_polynomial_name(shape):
    if shape == -1:
        return "unknown"
    if shape == 0:
        return "linear"
    if shape == 1:
        return str(shape) + "st degree polynomial"
    elif shape == 2:
        return str(shape) + "nd degree polynomial"
    elif shape == 3:
        return str(shape) + "rd degree polynomial"
    else:
        return str(shape) + "th degree polynomial"


def _plot(
    _poly,
    bounds=True,
    residuals=False,
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

    title = title or f"{_poly.pattern.name}"

    # prepare figure
    fig = plt.figure(constrained_layout=False, **kwargs)
    if residuals:
        gridspec = fig.add_gridspec(
            nrows=2, ncols=1, height_ratios=[5, 3], wspace=0, hspace=0
        )
        ax2 = fig.add_subplot(gridspec[1, 0], zorder=40)

        # residuals histogram
        ax2.hist(_poly.residuals.values, **bluebelt.config("pattern.residuals.hist"))
        ax2.set_yticks([])

        # get current limits
        xlims = ax2.get_xlim()
        ylims = ax2.get_ylim()

        # fit a normal distribution to the data
        norm_mu, norm_std = stats.norm.fit(_poly.residuals.dropna())
        pdf_x = np.linspace(xlims[0], xlims[1], 100)
        ax2.plot(
            pdf_x,
            stats.norm.pdf(pdf_x, norm_mu, norm_std),
            **bluebelt.config("pattern.residuals.normal"),
        )

        # histogram x label
        ax2.set_xlabel("residuals distribution")

        ax2.set_ylim(ylims[0], ylims[1] * 1.5)
        ax2.spines["left"].set_visible(False)
        ax2.spines["right"].set_visible(False)

        ax2.text(
            0.02,
            0.7,
            f"D'Agostino-Pearson\nstatistic: {_poly.statistic:1.2f}\np: {_poly.p_value:1.2f}",
            transform=ax2.transAxes,
            **bluebelt.config("pattern.statistics"),
        )
    else:
        gridspec = fig.add_gridspec(nrows=1, ncols=1)

    ax1 = fig.add_subplot(gridspec[0, 0], zorder=50)

    # pattern
    ax1.plot(
        _poly.pattern.index,
        _poly.pattern.values,
        label="pattern",
        **bluebelt.config("pattern.line"),
    )

    if bounds:
        # observations
        ax1.plot(
            _poly.pattern.index,
            _poly.within_bounds.values,
            label="observations",
            **bluebelt.config("pattern.observations"),
        )

        # bounds (fill between and dotted lines)
        ax1.fill_between(
            _poly.pattern.index,
            _poly.lower.values,
            _poly.upper.values,
            label=f"{(_poly.confidence * 100):1.0f}% bounds",
            **bluebelt.config("pattern.bounds.fill"),
        )
        ax1.plot(
            _poly.pattern.index,
            _poly.lower.values,
            label=None,
            **bluebelt.config("pattern.bounds.line"),
        )
        ax1.plot(
            _poly.pattern.index,
            _poly.upper.values,
            label=None,
            **bluebelt.config("pattern.bounds.line"),
        )

        # out of bounds
        ax1.plot(
            _poly.pattern.index,
            _poly.out_of_bounds.values,
            label="out of bounds",
            **bluebelt.config("pattern.out_of_bounds"),
        )
    else:
        # observations
        ax1.plot(
            _poly.pattern.index,
            _poly.within_bounds.values,
            label="observations",
            **bluebelt.config("pattern.observations"),
        )

        # out of bounds
        ax1.plot(
            _poly.pattern.index,
            _poly.out_of_bounds.values,
            label="out of bounds",
            **bluebelt.config("pattern.observations"),
        )

    # outliers
    ax1.plot(
        _poly.pattern.index,
        _poly.outliers.values,
        label="outliers",
        **bluebelt.config("pattern.outliers"),
    )

    # limit axis
    ax1.set_xlim(xlim)
    ax1.set_ylim(ylim)

    # set ticks
    if max_xticks is None:
        max_xticks = bluebelt.helpers.ticks.get_max_xticks(ax1)
    bluebelt.helpers.ticks.year_week(_poly.pattern, ax=ax1, max_xticks=max_xticks)

    # format ticks
    if format_xticks:
        ax1.set_xticks(ax1.get_xticks())
        ax1.set_xticklabels([f"{x:{format_xticks}}" for x in ax1.get_xticks()])
    if format_yticks:
        ax1.set_yticks(ax1.get_yticks())
        ax1.set_yticklabels([f"{y:{format_yticks}}" for y in ax1.get_yticks()])

    # labels
    if title:
        ax1.set_title(title)
    if xlabel:
        ax1.set_xlabel(xlabel)
    if ylabel:
        ax1.set_ylabel(ylabel)

    # legend
    if legend:
        ax1.legend()
    elif ax1.get_legend() is not None:
        ax1.get_legend().set_visible(False)

    plt.tight_layout()

    # file
    if path:
        if len(os.path.dirname(path)) > 0 and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig


def _frame_plot(
    _poly,
    bounds=True,
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

    title = title or "frame polynomials"

    # prepare figure
    fig = plt.figure(constrained_layout=False, **kwargs)
    gridspec = fig.add_gridspec(nrows=1, ncols=1)

    ax1 = fig.add_subplot(gridspec[0, 0], zorder=50)

    for id, column in enumerate(_poly._obj.columns):

        # pattern
        ax1.plot(
            _poly._pattern.index,
            _poly._pattern[column].values,
            label=str(column),
            **bluebelt.config(f"line{id%7}"),
        )  # line0 - line7

        if bounds:
            # bounds (fill between and dotted lines)
            ax1.fill_between(
                _poly._pattern.index,
                _poly._lower[column].values,
                _poly._upper[column].values,
                label=None,
                **bluebelt.config(f"fill{id%7}"),
            )

    # limit axis
    ax1.set_xlim(xlim)
    ax1.set_ylim(ylim)

    # set ticks
    if max_xticks is None:
        max_xticks = bluebelt.helpers.ticks.get_max_xticks(ax1)
    bluebelt.helpers.ticks.year_week(_poly.pattern, ax=ax1, max_xticks=max_xticks)

    # format ticks
    if format_xticks:
        ax1.set_xticks(ax1.get_xticks())
        ax1.set_xticklabels([f"{x:{format_xticks}}" for x in ax1.get_xticks()])
    if format_yticks:
        ax1.set_yticks(ax1.get_yticks())
        ax1.set_yticklabels([f"{y:{format_yticks}}" for y in ax1.get_yticks()])

    # labels
    if title:
        ax1.set_title(title)
    if xlabel:
        ax1.set_xlabel(xlabel)
    if ylabel:
        ax1.set_ylabel(ylabel)

    # legend
    if legend:
        ax1.legend()
    elif ax1.get_legend() is not None:
        ax1.get_legend().set_visible(False)

    plt.tight_layout()

    # file
    if path:
        if len(os.path.dirname(path)) > 0 and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig
