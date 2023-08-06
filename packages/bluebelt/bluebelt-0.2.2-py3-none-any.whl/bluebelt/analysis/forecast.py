import math
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

from bluebelt.helpers.ci import ci_mean
from bluebelt.helpers.decorators.performance import performance

import bluebelt.styles

import warnings
import os


@performance
class MAE:
    def __init__(self, frame, forecast=None, actuals=None, **kwargs):

        self.frame = frame
        self.forecast = forecast
        self.actuals = actuals
        self.calculate()

    def calculate(self):

        _set_forecast_and_actuals(self)

        if self.forecast is not None and self.actuals is not None:
            self.result = np.mean(np.abs(self.actuals - self.forecast))
            self.values = np.abs(self.actuals - self.forecast)
        else:
            self.result = None
            self.values = None

    def __repr__(self):
        return f"{self.__class__.__name__}(n={self.frame.shape[0]:1.0f}, result={self.result:1.4f})"

    def plot(
        self,
        xlim=(None, None),
        ylim=(None, None),
        bins=20,
        format_xticks="1.0f",
        title=None,
        xlabel=None,
        ylabel=None,
        path=None,
        **kwargs,
    ):
        return _plot(
            self,
            xlim=xlim,
            ylim=ylim,
            bins=bins,
            format_xticks=format_xticks,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            path=path,
            **kwargs,
        )


@performance
class MAPE:
    def __init__(self, frame, forecast=None, actuals=None, **kwargs):

        self.frame = frame
        self.forecast = forecast
        self.actuals = actuals
        self.calculate()

    def calculate(self):

        _set_forecast_and_actuals(self)

        if self.forecast is not None and self.actuals is not None:
            self.result = (
                np.abs((self.actuals - self.forecast) / self.actuals).sum()
            ) / len(self.forecast)
            self.values = np.abs((self.actuals - self.forecast) / self.actuals)
        else:
            self.result = None
            self.values = None

    def __repr__(self):
        return f"{self.__class__.__name__}(n={self.frame.shape[0]:1.0f}, result={self.result:1.4f})"

    def plot(
        self,
        xlim=(None, None),
        ylim=(None, None),
        bins=20,
        format_xticks="1.0%",
        title=None,
        xlabel=None,
        ylabel=None,
        path=None,
        **kwargs,
    ):
        return _plot(
            self,
            xlim=xlim,
            ylim=ylim,
            bins=bins,
            format_xticks=format_xticks,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            path=path,
            **kwargs,
        )


@performance
class SMAPE:
    def __init__(self, frame, forecast=None, actuals=None, adjust=True, **kwargs):

        self.frame = frame
        self.forecast = forecast
        self.actuals = actuals
        self.adjust = adjust
        self.calculate()

    def calculate(self):

        _set_forecast_and_actuals(self)

        if self.forecast is not None and self.actuals is not None:
            factor = 1 if self.adjust else 2
            self.result = (
                np.abs(self.actuals - self.forecast)
                / ((np.abs(self.actuals) + np.abs(self.forecast)) / factor)
            ).sum() / len(self.forecast)
            self.values = np.abs(self.actuals - self.forecast) / (
                (np.abs(self.actuals) + np.abs(self.forecast)) / factor
            )
        else:
            self.result = None
            self.values = None

    def __repr__(self):
        return f"{self.__class__.__name__}(adjust={self.adjust}, n={self.frame.shape[0]:1.0f}, result={self.result:1.4f})"

    def plot(
        self,
        xlim=(None, None),
        ylim=(None, None),
        bins=20,
        format_xticks="1.0%",
        title=None,
        xlabel=None,
        ylabel=None,
        path=None,
        **kwargs,
    ):
        return _plot(
            self,
            xlim=xlim,
            ylim=ylim,
            bins=bins,
            format_xticks=format_xticks,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            path=path,
            **kwargs,
        )


class MDA:
    def __init__(self, frame, forecast=None, actuals=None, **kwargs):

        self.frame = frame
        self.forecast = forecast
        self.actuals = actuals
        self.calculate()

    def calculate(self):

        _set_forecast_and_actuals(self)

        if self.forecast is not None and self.actuals is not None:
            self.result = (
                (
                    (self.forecast < self.forecast.shift(-1)).iloc[:-1]
                    == (self.actuals < self.actuals.shift(-1)).iloc[:-1]
                )
                * 1
            ).sum() / (len(self.forecast) - 1)
            self.values = (
                (self.forecast < self.forecast.shift(-1)).iloc[:-1]
                == (self.actuals < self.actuals.shift(-1)).iloc[:-1]
            ) * 1
        else:
            self.result = None
            self.values = None

    def __repr__(self):
        return f"{self.__class__.__name__}(n={self.frame.shape[0]:1.0f}, result={self.result:1.4f})"


@performance
class MPE:
    def __init__(self, frame, forecast=None, actuals=None, confidence=0.95, **kwargs):

        self.frame = frame
        self.forecast = forecast
        self.actuals = actuals
        self.confidence = confidence
        self.calculate()

    def calculate(self):

        _set_forecast_and_actuals(self)

        if self.forecast is not None and self.actuals is not None:
            self.values = (self.forecast - self.actuals) / self.actuals
            self.result = self.values.mean()
            self.ci_mean = ci_mean(self.values, confidence=self.confidence)
            self.ci_low, self.ci_high = self.ci_mean
            self.bias = not (self.ci_low <= 0 <= self.ci_high)
        else:
            self.result = None
            self.values = None

    def __repr__(self):
        return f"{self.__class__.__name__}(n={self.frame.shape[0]:1.0f}, result={self.result:1.4f}, ci_mean=({self.ci_low:1.4f}, {self.ci_high:1.4f}), bias={self.bias})"

    def plot(
        self,
        xlim=(None, None),
        ylim=(None, None),
        bins=20,
        format_xticks="1.0%",
        title=None,
        xlabel=None,
        ylabel=None,
        path=None,
        **kwargs,
    ):
        return _plot(
            self,
            xlim=xlim,
            ylim=ylim,
            bins=bins,
            format_xticks=format_xticks,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            path=path,
            **kwargs,
        )


@performance
class NFM:
    def __init__(self, frame, forecast=None, actuals=None, confidence=0.95, **kwargs):

        self.frame = frame
        self.forecast = forecast
        self.actuals = actuals
        self.confidence = confidence
        self.calculate()

    def calculate(self):

        _set_forecast_and_actuals(self)

        if (self.forecast < 0).any() or (self.actuals < 0).any():
            self.forecast = self.forecast[(self.forecast >= 0) & (self.actuals >= 0)]
            self.actuals = self.actuals[(self.forecast >= 0) & (self.actuals >= 0)]
            warnings.warn(
                "Forecast and actuals cannot contain negative values. The are deleted."
            )

        if self.forecast is not None and self.actuals is not None:
            self.values = pd.Series(
                (self.forecast - self.actuals) / (self.forecast + self.actuals),
                name="NFM values",
            )
            self.result = self.values.mean()
            self.ci_mean = ci_mean(self.values, confidence=self.confidence)
            self.ci_low, self.ci_high = self.ci_mean
            self.bias = not (self.ci_low <= 0 <= self.ci_high)
        else:
            self.result = None
            self.values = None

    def __repr__(self):
        return f"{self.__class__.__name__}(n={self.frame.shape[0]:1.0f}, result={self.result:1.4f}, ci_mean=({self.ci_low:1.4f}, {self.ci_high:1.4f}), bias={self.bias})"

    def plot(
        self,
        xlim=(None, None),
        ylim=(None, None),
        bins=20,
        format_xticks="1.0%",
        title=None,
        xlabel=None,
        ylabel=None,
        path=None,
        **kwargs,
    ):
        return _plot(
            self,
            xlim=xlim,
            ylim=ylim,
            bins=bins,
            format_xticks=format_xticks,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            path=path,
            **kwargs,
        )


def _set_forecast_and_actuals(_obj, **kwargs):
    if isinstance(_obj.frame, pd.Series):
        if isinstance(_obj.forecast, pd.Series):
            _obj.forecast = _obj.forecast
            _obj.actuals = _obj.frame
        elif isinstance(_obj.actuals, pd.Series):
            _obj.forecast = _obj.frame
            _obj.actuals = _obj.actuals
        else:
            raise ValueError(
                "Please provide forecast data or actuals data. One pandas Series is not enough to calculate forecast accuracy."
            )
    elif isinstance(_obj.frame, pd.DataFrame):
        if isinstance(_obj.forecast, str):
            _obj.forecast = _obj.frame[_obj.forecast]
        else:
            _obj.forecast = _obj.frame.iloc[:, 0]

        if isinstance(_obj.actuals, str):
            _obj.actuals = _obj.frame[_obj.actuals]
        else:
            _obj.actuals = _obj.frame.iloc[:, 1]
    return


def _plot(
    plot_obj,
    xlim=(None, None),
    ylim=(None, None),
    bins=20,
    format_stats=".2f",
    format_xticks=None,
    title=None,
    xlabel=None,
    ylabel=None,
    path=None,
    **kwargs,
):

    adjusted = " (adjusted)" if hasattr(plot_obj, "adjust") and plot_obj.adjust else ""
    title = title or f"{plot_obj.__class__.__name__}{adjusted}"

    # handle infinity
    values = plot_obj.values.replace([np.inf, -np.inf], np.nan)

    fig, ax = plt.subplots(
        nrows=1, ncols=1, gridspec_kw={"wspace": 0, "hspace": 0}, **kwargs
    )

    # plot
    ax.hist(values, bins=bins, **bluebelt.config("forecast.hist"))

    # ci mean
    if hasattr(plot_obj, "ci_mean"):
        ax.axvspan(
            plot_obj.ci_low,
            plot_obj.ci_high,
            label=f"CI mean ({plot_obj.ci_low:{format_stats}}, {plot_obj.ci_high:{format_stats}})",
            **bluebelt.config("forecast.ci_mean.span"),
        )
        ax.axvline(
            x=plot_obj.ci_low,
            ymin=0,
            ymax=1,
            **bluebelt.config("forecast.ci_mean.line"),
        )
        ax.axvline(
            x=plot_obj.ci_high,
            ymin=0,
            ymax=1,
            **bluebelt.config("forecast.ci_mean.line"),
        )
        ax.legend()

    if hasattr(plot_obj, "bias"):
        if plot_obj.bias:
            t = (
                "forecast is biased: forecast > actuals"
                if plot_obj.result > 0
                else "forecast is biased: forecast < actuals"
            )
        else:
            t = "forecast is not biased"
        ax.text(
            0.02,
            0.98,
            t,
            transform=ax.transAxes,
            **bluebelt.config("forecast.bias.text"),
        )

    # set xlim
    xlim_lower, xlim_upper = xlim
    xlim_lower = xlim_lower or math.floor(values.min())
    xlim_upper = xlim_upper or math.ceil(values.max())
    xlim = (xlim_lower, xlim_upper)
    ax.set_xlim(xlim)

    # remove yticks
    ax.set_yticks([])

    plt.tight_layout()

    # limit axis
    ax.set_ylim(ylim)

    # format ticks
    if format_xticks:
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels([f"{x:{format_xticks}}" for x in ax.get_xticks()])

    # labels
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    # file
    if path:
        if len(os.path.dirname(path)) > 0 and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig
