import os
import pandas as pd
import numpy as np

import bluebelt.helpers.ci
import bluebelt.helpers.boxplot

import scipy.stats as stats
import matplotlib.pyplot as plt
import math


def index():
    df = pd.DataFrame(
        [
            ["discrete", "discrete", "-", "-", "-", "chi square test", ""],
            ["discrete", "continuous", "-", "-", "-", "logistic regression", ""],
            [
                "continuous",
                "discrete",
                "mean",
                "1",
                "normal",
                "1 sample t-test",
                "one_sample_t",
            ],
            [
                "continuous",
                "discrete",
                "mean",
                "1",
                "non-normal",
                "1 sample Wilcoxon test",
                "wilcoxon",
            ],
            [
                "continuous",
                "discrete",
                "mean",
                "2",
                "normal",
                "2 sample t-test",
                "two_sample_t",
            ],
            [
                "continuous",
                "discrete",
                "mean",
                "2",
                "non-normal",
                "Mann-Whitney test",
                "mann_whitney",
            ],
            ["continuous", "discrete", "mean", ">2", "normal", "1 way Anova", "anova"],
            [
                "continuous",
                "discrete",
                "mean",
                ">2",
                "non-normal",
                "Kruskal-Wallis test",
                "kruskal",
            ],
            ["continuous", "discrete", "variance", "2", "normal", "F-test", "f_test"],
            [
                "continuous",
                "discrete",
                "variance",
                "2",
                "non-normal",
                "Levene’s test",
                "levene",
            ],
            [
                "continuous",
                "discrete",
                "variance",
                ">2",
                "normal",
                "Bartlett’s test",
                "bartlett",
            ],
            [
                "continuous",
                "discrete",
                "variance",
                ">2",
                "non-normal",
                "Levene’s test",
                "levene",
            ],
            ["continuous", "continuous", "", "-", "-", "regression", ""],
        ],
        columns=[
            "Y",
            "X",
            "investigate",
            "# data groups",
            "distribution",
            "test",
            "bluebelt",
        ],
    )
    print(df.to_string(index=False))


class OneSampleT:
    def __init__(
        self, frame, columns=None, popmean=None, confidence=0.95, alpha=0.05, **kwargs
    ):

        if not popmean:
            raise ValueError(
                "Please provide a value for the population mean. e.g. popmean=100"
            )

        if isinstance(frame, pd.Series):
            frame = pd.DataFrame(frame).dropna()
        elif isinstance(columns, str):
            frame = frame[columns].dropna()
        elif isinstance(columns, list):
            frame = frame[columns[:1]].dropna()
        else:
            frame = frame.iloc[:, :1].dropna()

        self.frame = frame
        self.nrows = frame.shape[0]
        self.ncols = 1
        self.popmean = popmean
        self.confidence = confidence
        self.alpha = alpha
        self.test = "One Sample t-Test"
        self.h0 = f"$H_0: \\bar{{X}} = \\mu$"
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.statistic, self.p_value = stats.ttest_1samp(
            a=self.frame.iloc[:, 0].values, popmean=self.popmean, **kwargs
        )
        self.ci_mean = bluebelt.helpers.ci.ci_mean(self.frame.iloc[:, 0])
        self.passed = True if self.p_value > self.alpha else False

    def __str__(self):
        _result = f"-" * (len(self.test) + 12) + "\n"
        _result += f"  {self.test} results\n"
        _result += f"-" * (len(self.test) + 12) + "\n"
        _result += f"\n"

        _result += f"input variables\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"observations:":<30}{self.nrows:1.0f}\n'
        _result += f'  {"confidence:":<30}{self.confidence}\n'
        _result += f'  {"alpha:":<30}{self.alpha}\n'
        _result += f'  {"population mean:":<30}{self.popmean}\n'

        _result += f"\n"
        _result += f"result\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"statistic:":<30}{self.statistic:1.4f}\n'
        _result += f'  {"p-value:":<30}{self.p_value:1.4f}\n'
        _result += f'  {"passed:":<30}{self.passed}\n'
        return _result

    def __repr__(self):
        return f"{self.__class__.__name__}(nrows={self.nrows}, confidence={self.confidence}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})"

    def result(self):
        print(self.statistic)

    def plot(
        self,
        xlim=(None, None),
        format_xticks=None,
        format_stats=".2f",
        format_means=".2f",
        title=None,
        xlabel=None,
        ylabel=None,
        legend=True,
        path=None,
        **kwargs,
    ):
        return _equal_means_plot(
            self,
            xlim=xlim,
            format_xticks=format_xticks,
            format_stats=format_stats,
            format_means=format_means,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            legend=legend,
            path=path,
            **kwargs,
        )


class Wilcoxon:
    """
    Calculate the Wilcoxon signed-rank test.

    The Wilcoxon signed-rank test tests the null hypothesis that two related paired samples come from the same distribution.
    In particular, it tests whether the distribution of the differences x - y is symmetric about zero.
    It is a non-parametric version of the paired T-test.
    This test is performed with the assumption that if a pandas Series is provided the series contains the differences between x and y.
    """

    def __init__(self, frame, columns=None, confidence=0.95, alpha=0.05, **kwargs):

        if isinstance(frame, pd.Series):
            frame = pd.DataFrame(frame)
        elif isinstance(columns, str):
            frame = frame[columns]
        elif isinstance(columns, list):
            frame = frame[columns[:2]]
        else:
            frame = frame.iloc[:, :2]

        self.frame = frame
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.confidence = confidence
        self.alpha = alpha
        self.test = "Wilcoxon Signed-Rank Test"
        self.h0 = f"$H_0:$" + "difference has symmetric distribution around zero"
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.array_a = self.frame.iloc[:, 0].dropna()
        self.array_b = self.frame.iloc[:, 1].dropna() if self.ncols == 2 else None
        self.statistic, self.p_value = stats.wilcoxon(
            x=self.array_a, y=self.array_b, **kwargs
        )
        self.passed = True if self.p_value > self.alpha else False

    def __str__(self):
        _result = f"-" * (len(self.test) + 12) + "\n"
        _result += f"  {self.test} results\n"
        _result += f"-" * (len(self.test) + 12) + "\n"
        _result += f"\n"

        _result += f"input variables\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"observations:":<30}{self.nrows:1.0f}\n'
        _result += f'  {"confidence:":<30}{self.confidence}\n'
        _result += f'  {"alpha:":<30}{self.alpha}\n'

        _result += f"\n"
        _result += f"result\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"statistic:":<30}{self.statistic:1.4f}\n'
        _result += f'  {"p-value:":<30}{self.p_value:1.4f}\n'
        _result += f'  {"passed:":<30}{self.passed}\n'
        return _result

    def __repr__(self):
        return f"{self.__class__.__name__}(nrows={self.nrows}, confidence={self.confidence}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})"

    def plot(
        self,
        xlim=(None, None),
        format_xticks=None,
        format_stats=".2f",
        format_means=".2f",
        title=None,
        xlabel=None,
        ylabel=None,
        legend=True,
        path=None,
        **kwargs,
    ):
        return _equal_means_plot(
            self,
            xlim=xlim,
            format_xticks=format_xticks,
            format_stats=format_stats,
            format_means=format_means,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            legend=legend,
            path=path,
            **kwargs,
        )


class TwoSampleT:
    def __init__(
        self, frame, columns=None, related=False, confidence=0.95, alpha=0.05, **kwargs
    ):

        if isinstance(columns, list):
            frame = frame[columns[:2]]
        else:
            frame = frame.iloc[:, :2]

        self.frame = frame
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.related = related
        self.confidence = confidence
        self.alpha = alpha
        self.test = "Two Sample t-Test"
        self.h0 = _get_h0_equal_means(self.frame.columns)
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.array_a = self.frame.iloc[:, 0].dropna()
        self.array_b = self.frame.iloc[:, 1].dropna()

        self.mean_a = self.array_a.mean()
        self.mean_b = self.array_b.mean()

        self.max_a = self.array_a.max()
        self.max_b = self.array_b.max()

        self.min_a = self.array_a.min()
        self.min_b = self.array_b.min()

        self.ci_mean_a = bluebelt.helpers.ci.ci_mean(self.array_a)
        self.ci_mean_b = bluebelt.helpers.ci.ci_mean(self.array_b)

        # related or not
        if self.related:
            statistic, pvalue = stats.ttest_rel(self.array_a, self.array_b, **kwargs)
        else:
            # test equal variance
            equal_var = (
                True if Levene(frame=self.frame, alpha=self.alpha).passed else False
            )
            statistic, pvalue = stats.ttest_ind(
                self.array_a, self.array_b, equal_var=equal_var, **kwargs
            )

        self.statistic = statistic
        self.p_value = pvalue
        self.passed = True if self.p_value >= self.alpha else False

    def __str__(self):
        _result = f"-" * (len(self.test) + 12) + "\n"
        _result += f"  {self.test} results\n"
        _result += f"-" * (len(self.test) + 12) + "\n"
        _result += f"\n"

        _result += f"input variables\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"observations:":<30}{self.nrows:1.0f}\n'
        _result += f'  {"confidence:":<30}{self.confidence}\n'
        _result += f'  {"alpha:":<30}{self.alpha}\n'

        _result += f"\n"
        _result += f"result\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"statistic:":<30}{self.statistic:1.4f}\n'
        _result += f'  {"p-value:":<30}{self.p_value:1.4f}\n'
        _result += f'  {"passed:":<30}{self.passed}\n'
        return _result

    def __repr__(self):
        return f"{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, confidence={self.confidence}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})"

    def result(self):
        print(self.statistic)

    def plot(
        self,
        xlim=(None, None),
        format_xticks=None,
        format_stats=".2f",
        format_means=".2f",
        title=None,
        xlabel=None,
        ylabel=None,
        legend=True,
        path=None,
        **kwargs,
    ):
        return _equal_means_plot(
            self,
            xlim=xlim,
            format_xticks=format_xticks,
            format_stats=format_stats,
            format_means=format_means,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            legend=legend,
            path=path,
            **kwargs,
        )


class MannWhitney:
    """
    apply the Mann-Whitney test on a pandas dataframe with the columns as groups to compare
    Returns the scipy Mann-Whitney; statistic, pvalue
    pvalue >= alpha (default 0.05) : columns have equal means
    pvalue < alpha: columns don't have equal means
    """

    def __init__(self, frame, columns=None, confidence=0.95, alpha=0.05, **kwargs):

        if isinstance(columns, list):
            frame = frame[columns[:2]]
        else:
            frame = frame.iloc[:, :2]

        self.frame = frame
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.confidence = confidence
        self.alpha = alpha
        self.test = "Mann-Whitney"
        self.h0 = _get_h0_equal_means(self.frame.columns)
        self.calculate(**kwargs)

    def calculate(self, **kwargs):

        self.array_a = self.frame.iloc[:, 0].dropna().values
        self.array_b = self.frame.iloc[:, 1].dropna().values

        self.statistic, self.p_value = stats.mannwhitneyu(self.array_a, self.array_b)
        self.passed = True if self.p_value >= self.alpha else False

    def __str__(self):
        _result = f"-" * (len(self.test) + 12) + "\n"
        _result += f"  {self.test} results\n"
        _result += f"-" * (len(self.test) + 12) + "\n"
        _result += f"\n"

        _result += f"input variables\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"observations:":<30}{self.nrows:1.0f}\n'
        _result += f'  {"confidence:":<30}{self.confidence}\n'
        _result += f'  {"alpha:":<30}{self.alpha}\n'

        _result += f"\n"
        _result += f"result\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"statistic:":<30}{self.statistic:1.4f}\n'
        _result += f'  {"p-value:":<30}{self.p_value:1.4f}\n'
        _result += f'  {"passed:":<30}{self.passed}\n'
        return _result

    def __repr__(self):
        return f"{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, confidence={self.confidence}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})"

    def plot(
        self,
        xlim=(None, None),
        format_xticks=None,
        format_stats=".2f",
        format_means=".2f",
        title=None,
        xlabel=None,
        ylabel=None,
        legend=True,
        path=None,
        **kwargs,
    ):
        return _equal_means_plot(
            self,
            xlim=xlim,
            format_xticks=format_xticks,
            format_stats=format_stats,
            format_means=format_means,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            legend=legend,
            path=path,
            **kwargs,
        )


class Anova:
    """
    apply the one way ANOVA test on a pandas dataframe with the columns as groups to compare
    Returns the scipy F_onewayResult; statistic, pvalue
    pvalue >= alpha (default 0.05) : columns have equal means
    pvalue < alpha: columns don't have equal means
    """

    def __init__(self, frame, columns=None, confidence=0.95, alpha=0.05, **kwargs):

        self.frame = frame if columns is None else frame[columns]
        self.data_dict = _data_dict(self.frame)
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.confidence = confidence
        self.alpha = alpha
        self.test = "ANOVA"
        self.h0 = _get_h0_equal_means(self.frame.columns)
        self.calculate(**kwargs)

    def calculate(self, **kwargs):

        self.statistic, self.p_value = stats.f_oneway(*self.data_dict.values())
        self.passed = True if self.p_value >= self.alpha else False

    def __repr__(self):
        return f"{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})"

    def plot(
        self,
        xlim=(None, None),
        format_xticks=None,
        format_stats=".2f",
        format_means=".2f",
        title=None,
        xlabel=None,
        ylabel=None,
        legend=True,
        path=None,
        **kwargs,
    ):
        return _equal_means_plot(
            self,
            xlim=xlim,
            format_xticks=format_xticks,
            format_stats=format_stats,
            format_means=format_means,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            legend=legend,
            path=path,
            **kwargs,
        )


class KruskalWallis:
    """
    apply the Kruskal-Wallis test on a pandas dataframe with the columns as groups to compare
    Returns the scipy KruskalResult; statistic, pvalue
    pvalue >= alpha (default 0.05) : columns have equal means
    pvalue < alpha: columns don't have equal means
    """

    def __init__(self, frame, columns=None, confidence=0.95, alpha=0.05, **kwargs):

        self.frame = frame if columns is None else frame[columns]
        self.data_dict = _data_dict(self.frame)
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.confidence = confidence
        self.alpha = alpha
        self.test = "Kruskal-Wallis"
        self.h0 = _get_h0_equal_means(self.frame.columns)
        self.calculate(**kwargs)

    def calculate(self, **kwargs):

        self.statistic, self.p_value = stats.kruskal(*self.data_dict.values())
        self.passed = True if self.p_value >= self.alpha else False

    def __str__(self):
        _result = f"-" * (len(self.test) + 12) + "\n"
        _result += f"  {self.test} results\n"
        _result += f"-" * (len(self.test) + 12) + "\n"
        _result += f"\n"

        _result += f"input variables\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"observations:":<30}{self.nrows:1.0f}\n'
        _result += f'  {"confidence:":<30}{self.confidence}\n'
        _result += f'  {"alpha:":<30}{self.alpha}\n'

        _result += f"\n"
        _result += f"result\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"statistic:":<30}{self.statistic:1.4f}\n'
        _result += f'  {"p-value:":<30}{self.p_value:1.4f}\n'
        _result += f'  {"passed:":<30}{self.passed}\n'
        return _result

    def __repr__(self):
        return f"{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, confidence={self.confidence}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})"

    def plot(
        self,
        xlim=(None, None),
        format_xticks=None,
        format_stats=".2f",
        format_means=".2f",
        title=None,
        xlabel=None,
        ylabel=None,
        legend=True,
        path=None,
        **kwargs,
    ):
        return _equal_means_plot(
            self,
            xlim=xlim,
            format_xticks=format_xticks,
            format_stats=format_stats,
            format_means=format_means,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            legend=legend,
            path=path,
            **kwargs,
        )


class EqualMeans:
    """
    Test a dataframe for equal means over the dataframe columns.

    frame: a pandas DataFrame
    columns: string or list of strings with the column names to be tested
    alpha: test threshold

    applies ANOVA or Kruskal-Wallis test

    pvalue >= alpha (default 0.05) : columns have equal means
    pvalue < alpha: columns don't have equal means

    """

    def __init__(self, frame, columns=None, confidence=0.95, alpha=0.05, **kwargs):

        self.frame = frame if columns is None else frame[columns]
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.confidence = confidence
        self.alpha = alpha
        self.h0 = _get_h0_equal_means(self.frame.columns)
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        # test for normal distribution; null hypothesis: values come from a normal distribution
        if (
            NormalDistribution(frame=self.frame, alpha=self.alpha).passed
            and Levene(frame=self.frame, alpha=self.alpha).passed
        ):
            # all columns in the dataframe come from a normal distribution AND have equal variances
            # do Anova
            test = Anova(frame=self.frame, alpha=self.alpha)
        else:
            # not all columns in the dataframe come from a normal distribution OR have equal variances
            # do Kruskal-Wallis
            test = KruskalWallis(frame=self.frame, alpha=self.alpha)

        self.test = test.test
        self.statistic = test.statistic
        self.p_value = test.p_value
        self.passed = True if self.p_value >= self.alpha else False

    def __str__(self):
        _result = f"-" * (len(self.test) + 12) + "\n"
        _result += f"  {self.test} results\n"
        _result += f"-" * (len(self.test) + 12) + "\n"
        _result += f"\n"

        _result += f"input variables\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"observations:":<30}{self.nrows:1.0f}\n'
        _result += f'  {"confidence:":<30}{self.confidence}\n'
        _result += f'  {"alpha:":<30}{self.alpha}\n'

        _result += f"\n"
        _result += f"result\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"statistic:":<30}{self.statistic:1.4f}\n'
        _result += f'  {"p-value:":<30}{self.p_value:1.4f}\n'
        _result += f'  {"passed:":<30}{self.passed}\n'
        return _result

    def __repr__(self):
        return f"{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})"

    def plot(
        self,
        xlim=(None, None),
        format_xticks=None,
        format_stats=".2f",
        format_means=".2f",
        title=None,
        xlabel=None,
        ylabel=None,
        legend=True,
        path=None,
        **kwargs,
    ):
        return _equal_means_plot(
            self,
            xlim=xlim,
            format_xticks=format_xticks,
            format_stats=format_stats,
            format_means=format_means,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            legend=legend,
            path=path,
            **kwargs,
        )


def _equal_means_plot(
    plot_obj,
    xlim=(None, None),
    format_xticks=None,
    format_stats=".2f",
    format_means=".2f",
    title=None,
    xlabel=None,
    ylabel=None,
    legend=True,
    path=None,
    **kwargs,
):

    title = title or f"{plot_obj.test}"

    # prepare figure
    fig, axes = plt.subplots(
        nrows=plot_obj.ncols,
        ncols=1,
        sharex=True,
        gridspec_kw={"wspace": 0, "hspace": 0},
        **kwargs,
    )

    for row in range(0, plot_obj.ncols):

        if plot_obj.ncols == 1:
            ax = axes
        else:
            ax = axes[row]

        # set right zorder
        ax.set_zorder((plot_obj.ncols - row) * 10)
        # get the data
        array = plot_obj.frame.iloc[:, row].dropna()

        # 1. box plot ############################################
        boxplot = ax.boxplot(array, vert=False, widths=0.3, whis=1.5)
        for box in boxplot["boxes"]:
            box.set(**bluebelt.config("equal_means.boxplot.boxes"))

        # 2. CI for the mean #####################################
        ci_mean = bluebelt.helpers.ci.ci_mean(array, confidence=plot_obj.confidence)

        ax.plot(
            [ci_mean[0], ci_mean[1]],
            [1.5, 1.5],
            **bluebelt.config("equal_means.ci_mean.line"),
        )
        ax.axvline(
            x=ci_mean[0],
            ymin=9 / 14,
            ymax=11 / 14,
            **bluebelt.config("equal_means.ci_mean.vline"),
        )
        ax.axvline(
            x=ci_mean[1],
            ymin=9 / 14,
            ymax=11 / 14,
            **bluebelt.config("equal_means.ci_mean.vline"),
        )
        ax.scatter([array.mean()], [1.5], **bluebelt.config("equal_means.ci_mean.mean"))

        # fill the CI area
        ci_area = np.linspace(ci_mean[0], ci_mean[1], 100)
        ax.fill_between(
            x=(ci_mean[0], ci_mean[1]),
            y1=0,
            y2=2,
            label="CI sample mean",
            **bluebelt.config("equal_means.ci_mean.fill"),
        )
        ax.axvline(
            x=ci_mean[0], ymin=0, ymax=2, **bluebelt.config("equal_means.ci_mean.vline")
        )
        ax.axvline(
            x=ci_mean[1], ymin=0, ymax=2, **bluebelt.config("equal_means.ci_mean.vline")
        )

        # plot CI values
        ax.text(
            ci_mean[0],
            1.5,
            f"{ci_mean[0]:{format_means}} ",
            **bluebelt.config("equal_means.ci_mean.min_text"),
        )
        ax.text(
            ci_mean[1],
            1.5,
            f" {ci_mean[1]:{format_means}}",
            **bluebelt.config("equal_means.ci_mean.max_text"),
        )

        # plot popmean if it exists
        if hasattr(plot_obj, "popmean"):
            ax.axvline(
                plot_obj.popmean,
                ymin=0,
                ymax=2,
                label="population mean",
                **bluebelt.config("equal_means.popmean.line"),
            )

        ax.set_ylim([0.25, 2])
        ax.set_yticklabels([array.name])

        # set title and legend
        if row == 0:
            ax.set_title(
                plot_obj.h0
                + f"   t={plot_obj.statistic:{format_stats}} p={plot_obj.p_value:{format_stats}} ("
                + r"$H_0$"
                + f' is {"accepted" if plot_obj.p_value > plot_obj.alpha else "rejected"})',
                **bluebelt.config("equal_means.title"),
            )
            # legend
            if legend:
                ax.legend()
            elif ax.get_legend() is not None:
                ax.get_legend().set_visible(False)
        elif ax.get_legend() is not None:
            ax.get_legend().set_visible(False)

    # format things
    if plot_obj.ncols == 1:
        ax = axes
    else:
        ax = axes[-1]

    # limit axis
    ax.set_xlim(xlim)

    # format ticks
    if format_xticks:
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels([f"{x:{format_xticks}}" for x in ax.get_xticks()])

    # labels
    if title:
        fig.suptitle(
            t=title, x=fig.subplotpars.left, **bluebelt.config("equal_means.suptitle")
        )

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    plt.tight_layout()

    # and again
    if title:
        fig.suptitle(
            t=title, x=fig.subplotpars.left, **bluebelt.config("equal_means.suptitle")
        )

    # file
    if path:
        if len(os.path.dirname(path)) > 0 and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig


# equal variance
class FTest:
    """
    apply the F-test on a pandas dataframe with the columns as groups to compare
    the F-test is extremely sensitive to non-normality of the two arrays
    pvalue >= 0.05 : columns have equal variances
    pvalue < 0.05: columns don't have equal variances
    """

    def __init__(self, frame, columns=None, alpha=0.05, **kwargs):

        self.frame = frame if columns is None else frame[columns]
        self.columms = columns
        self.array_a = self.frame.iloc[:, 0].dropna()
        self.array_b = self.frame.iloc[:, 1].dropna()
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.alpha = alpha
        self.test = "F-test"
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.statistic = self.array_a.var() / self.array_b.var()
        self.p_value = stats.f.cdf(
            self.statistic, self.array_a.size - 1, self.array_b.size - 1
        )
        self.passed = True if self.p_value >= self.alpha else False

    def __str__(self):
        _result = f"-" * (len(self.test) + 12) + "\n"
        _result += f"  {self.test} results\n"
        _result += f"-" * (len(self.test) + 12) + "\n"
        _result += f"\n"

        _result += f"input variables\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"observations:":<30}{self.nrows:1.0f}\n'
        _result += f'  {"alpha:":<30}{self.alpha}\n'

        _result += f"\n"
        _result += f"result\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"statistic:":<30}{self.statistic:1.4f}\n'
        _result += f'  {"p-value:":<30}{self.p_value:1.4f}\n'
        _result += f'  {"passed:":<30}{self.passed}\n'
        return _result

    def __repr__(self):
        return f"{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})"

    def plot(self, **kwargs):
        return _equal_variances_plot(self, **kwargs)


class Levene:
    """
    apply levene's test on a pandas dataframe with the columns as groups to compare
    Returns the scipy LeveneResult; statistic, pvalue
    pvalue >= 0.05 : columns have equal variances
    pvalue < 0.05: columns don't have equal variances
    """

    def __init__(self, frame, columns=None, alpha=0.05, **kwargs):

        self.frame = frame if columns is None else frame[columns]
        self.data_dict = _data_dict(self.frame)
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.alpha = alpha
        self.test = "Levene"
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.statistic, self.p_value = stats.levene(*self.data_dict.values())
        self.passed = True if self.p_value >= self.alpha else False

    def __str__(self):
        _result = f"-" * (len(self.test) + 12) + "\n"
        _result += f"  {self.test} results\n"
        _result += f"-" * (len(self.test) + 12) + "\n"
        _result += f"\n"

        _result += f"input variables\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"observations:":<30}{self.nrows:1.0f}\n'
        _result += f'  {"alpha:":<30}{self.alpha}\n'

        _result += f"\n"
        _result += f"result\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"statistic:":<30}{self.statistic:1.4f}\n'
        _result += f'  {"p-value:":<30}{self.p_value:1.4f}\n'
        _result += f'  {"passed:":<30}{self.passed}\n'
        return _result

    def __repr__(self):
        return f"{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})"

    def plot(self, **kwargs):
        return _equal_variances_plot(self, **kwargs)


class Bartlett:
    """
    apply Bartlett's test on a pandas dataframe with the columns as groups to compare
    Returns the scipy BartlettResult; statistic, pvalue
    pvalue >= 0.05 : columns have equal variances
    pvalue < 0.05: columns don't have equal variances
    """

    def __init__(self, frame, columns=None, alpha=0.05, **kwargs):

        self.frame = frame if columns is None else frame[columns]
        self.data_dict = _data_dict(self.frame)
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.alpha = alpha
        self.test = "Bartlett"
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.statistic, self.p_value = stats.bartlett(*self.data_dict.values())
        self.passed = True if self.p_value >= self.alpha else False

    def __str__(self):
        _result = f"-" * (len(self.test) + 12) + "\n"
        _result += f"  {self.test} results\n"
        _result += f"-" * (len(self.test) + 12) + "\n"
        _result += f"\n"

        _result += f"input variables\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"observations:":<30}{self.nrows:1.0f}\n'
        _result += f'  {"alpha:":<30}{self.alpha}\n'

        _result += f"\n"
        _result += f"result\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"statistic:":<30}{self.statistic:1.4f}\n'
        _result += f'  {"p-value:":<30}{self.p_value:1.4f}\n'
        _result += f'  {"passed:":<30}{self.passed}\n'
        return _result

    def __repr__(self):
        return f"{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})"

    def plot(self, **kwargs):
        return _equal_variances_plot(self, **kwargs)


class EqualVariances:
    """
    Test a dataframe for equal variances over the dataframe columns.

    frame: a pandas DataFrame
    columns: string or list of strings with the column names to be tested
    alpha: test threshold

    applies F-test, Bartlett's or Levene's

    pvalue >= alpha (default 0.05) : columns have equal variances
    pvalue < alpha: columns don't have equal variances

    """

    def __init__(self, frame, columns=None, alpha=0.05, **kwargs):

        self.frame = frame if columns is None else frame[columns]
        self.columms = columns
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.alpha = alpha
        self.calculate(**kwargs)

    def calculate(self, **kwargs):

        # test for normal distribution; null hypothesis: values come from a normal distribution
        if NormalDistribution(frame=self.frame, alpha=self.alpha).passed:
            # all columns in the dataframe come from a normal distribution
            if self.ncols == 2:
                test = FTest(frame=self.frame, alpha=self.alpha)
            else:
                test = Bartlett(frame=self.frame, alpha=self.alpha)
        else:
            # not all columns in the dataframe come from a normal distribution
            test = Levene(frame=self.frame, alpha=self.alpha)

        self.test = test.test
        self.statistic = test.statistic
        self.p_value = test.p_value
        self.passed = True if self.p_value >= self.alpha else False

    def __str__(self):
        _result = f"-" * (len(self.test) + 12) + "\n"
        _result += f"  {self.test} results\n"
        _result += f"-" * (len(self.test) + 12) + "\n"
        _result += f"\n"

        _result += f"input variables\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"observations:":<30}{self.nrows:1.0f}\n'
        _result += f'  {"alpha:":<30}{self.alpha}\n'

        _result += f"\n"
        _result += f"result\n"
        _result += f"-" * 50 + "\n"
        _result += f'  {"statistic:":<30}{self.statistic:1.4f}\n'
        _result += f'  {"p-value:":<30}{self.p_value:1.4f}\n'
        _result += f'  {"passed:":<30}{self.passed}\n'
        return _result

    def __repr__(self):
        return f"{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})"

    def plot(self, **kwargs):
        return _equal_variances_plot(self, **kwargs)


def _equal_variances_plot(
    plot_obj,
    bins=20,
    xlim=(None, None),
    format_stats=".2f",
    format_xticks=None,
    title=None,
    xlabel=None,
    path=None,
    **kwargs,
):

    title = title or f"{plot_obj.test}"
    # prepare figure
    fig, axes = plt.subplots(
        nrows=plot_obj.ncols,
        ncols=1,
        sharex="col",
        gridspec_kw={"wspace": 0, "hspace": 0},
        **kwargs,
    )

    for row in range(0, plot_obj.ncols):

        if plot_obj.ncols == 1:
            ax = axes
        else:
            ax = axes[row]

        # set right zorder
        ax.set_zorder((plot_obj.ncols - row) * 10)
        # get the data
        array = plot_obj.frame.iloc[:, row]

        # calculate bin width
        bin_width = (
            np.nanmax(plot_obj.frame.values) - np.nanmin(plot_obj.frame.values)
        ) / bins

        # 1. histogram ############################################
        ax.hist(
            array,
            bins=np.arange(
                np.nanmin(plot_obj.frame.values),
                np.nanmax(plot_obj.frame.values) + bin_width,
                bin_width,
            ),
            **bluebelt.config("equal_variances.hist"),
        )
        ax.set_yticks([])
        ax.set_ylabel(array.name, **bluebelt.config("equal_variances.text"))

        if row == 0:
            ax.set_title(
                f"t={plot_obj.statistic:{format_stats}} p={plot_obj.p_value:{format_stats}} ("
                + r"$H_0$"
                + f' is {"accepted" if plot_obj.p_value > plot_obj.alpha else "rejected"})',
                **bluebelt.config("equal_variances.title"),
            )

    # format things
    if plot_obj.ncols == 1:
        ax = axes
    else:
        ax = axes[-1]

    # limit axis
    ax.set_xlim(xlim)

    # format ticks
    if format_xticks:
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels([f"{x:{format_xticks}}" for x in ax.get_xticks()])

    # labels
    if title:
        # add suptitle
        fig.suptitle(
            t=title,
            x=fig.subplotpars.left,
            **bluebelt.config("equal_variances.suptitle"),
        )
    if xlabel:
        ax.set_xlabel(xlabel)

    plt.tight_layout()

    # and again
    if title:
        # add suptitle
        fig.suptitle(
            t=title,
            x=fig.subplotpars.left,
            **bluebelt.config("equal_variances.suptitle"),
        )

    # file
    if path:
        if len(os.path.dirname(path)) > 0 and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig


# distribution
class AndersonDarling:
    """
    Anderson-Darling test

    null hypothesis: x comes from a normal distribution

    test all pandas dataframe columns for normal distribution
    input pivoted dataframe

    pvalue >= alpha : column values are (all) normally distributed
    pvalue < alpha: column values are not (all) normally distributed
    """

    def __init__(self, frame, dist="norm", alpha=0.05, **kwargs):

        if isinstance(frame, pd.Series):
            frame = pd.DataFrame(frame)

        # check arguments

        self.frame = frame
        self.dist = dist
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.alpha = alpha
        self.test = "Anderson-Darling"
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        statistics = {}
        p_values = {}
        passed_values = {}

        for col in self.frame.columns:

            AD, critical_values, significance_level = stats.anderson(
                self.frame[col].dropna().values, dist=self.dist
            )

            AD_adjusted = AD * (1 + (0.75 / 50) + 2.25 / (50**2))
            if AD_adjusted >= 0.6:
                pval = math.exp(
                    1.2937 - 5.709 * AD_adjusted - 0.0186 * (AD_adjusted**2)
                )
            elif AD_adjusted >= 0.34:
                pval = math.exp(
                    0.9177 - 4.279 * AD_adjusted - 1.38 * (AD_adjusted**2)
                )
            elif AD_adjusted > 0.2:
                pval = 1 - math.exp(
                    -8.318 + 42.796 * AD_adjusted - 59.938 * (AD_adjusted**2)
                )
            else:
                pval = 1 - math.exp(
                    -13.436 + 101.14 * AD_adjusted - 223.73 * (AD_adjusted**2)
                )

            statistics[col] = AD
            p_values[col] = pval
            passed_values[col] = True if pval >= self.alpha else False

        self.statistics = pd.Series(statistics)
        self.p_values = pd.Series(p_values)
        self.passed_values = pd.Series(passed_values)

        self.statistic = self.statistics[self.p_values.idxmin()]
        self.p_value = self.p_values.min()
        self.passed = True if self.p_value >= self.alpha else False

    def __repr__(self):
        return f"{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})"

    def plot(self, format_stats=".2f", title=None, path=None, **kwargs):
        return _distribution_plot(
            self, format_stats=format_stats, title=title, path=path, **kwargs
        )


class DAgostinoPearson:
    """
    D’Agostino-Pearson test

    null hypothesis: x comes from a normal distribution

    test all pandas dataframe columns for normal distribution
    input pivoted dataframe
    Returns the scipy NormaltestResult; statistic, pvalue for a single column
    Returns the worst scipy NormaltestResult as a tuple; statistic, pvalue for multiple columns
    pvalue >= alpha : column values are (all) normally distributed
    pvalue < alpha: column values are not (all) normally distributed
    """

    def __init__(self, frame, alpha=0.05, **kwargs):

        if isinstance(frame, pd.Series):
            frame = pd.DataFrame(frame)

        self.frame = frame
        self.dist = "norm"
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.alpha = alpha
        self.test = "D’Agostino-Pearson"
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        statistics = {}
        p_values = {}
        passed_values = {}

        statistic = 0
        p_value = 1

        for col in self.frame.columns:
            result = stats.normaltest(self.frame[col].dropna().values)
            if result.pvalue < p_value:
                p_value = result.pvalue
                statistic = result.statistic

            statistics[col] = result.statistic
            p_values[col] = result.pvalue
            passed_values[col] = True if result.pvalue >= self.alpha else False

        self.statistics = pd.Series(statistics)
        self.p_values = pd.Series(p_values)
        self.passed_values = pd.Series(passed_values)

        self.statistic = self.statistics[self.p_values.idxmin()]
        self.p_value = self.p_values.min()
        self.passed = True if self.p_value >= self.alpha else False

    def __repr__(self):
        return f"{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, alpha={self.alpha}, p_value={self.p_value:1.2f}, passed={self.passed})"

    def plot(self, format_stats=".2f", title=None, path=None, **kwargs):
        return _distribution_plot(
            self, format_stats=format_stats, title=title, path=path, **kwargs
        )


NormalDistribution = DAgostinoPearson


def _distribution_plot(_obj, format_stats=".2f", title=None, path=None, **kwargs):

    title = title or f"{_obj.test} ({_get_distribution(_obj.dist)} distribution)"

    # prepare figure
    ncols = math.ceil(math.sqrt(_obj.ncols))
    nrows = math.ceil(_obj.ncols / ncols)

    fig, axes = plt.subplots(
        nrows=nrows, ncols=ncols, gridspec_kw={"wspace": 0, "hspace": 0}, **kwargs
    )

    for row in range(0, nrows):
        for col in range(0, ncols):
            id = col + (ncols * row)

            if nrows == 1:
                if ncols == 1:
                    ax = axes
                else:
                    ax = axes[col]
            else:
                ax = axes[row, col]

            # get the data
            if id < _obj.ncols:
                array = _obj.frame.iloc[:, id].dropna()
                col = _obj.frame.columns[id]

                # H0 the two distributions are identical, F(x)=G(x)
                parameters = eval("stats." + _obj.dist + ".fit(array.values)")
                (osm, osr), (slope, intercept, r) = stats.probplot(
                    array, dist=eval("stats." + _obj.dist), sparams=parameters, fit=True
                )

                # plot
                ax.plot(osm, osr, **bluebelt.config("distribution_plot.dots"))
                ax.plot(
                    osm,
                    osm * slope + intercept,
                    **bluebelt.config("distribution_plot.line"),
                )

                # stats
                ax.text(
                    0.98,
                    0.02,
                    f"statistic: {_obj.statistics[col]:{format_stats}}\np-value: {_obj.p_values[col]:{format_stats}}",
                    transform=ax.transAxes,
                    **bluebelt.config("distribution_plot.stats"),
                )

                # plot name
                if _obj.ncols > 1:
                    ax.text(
                        0.02,
                        0.98,
                        f"{_obj.frame.columns[id]}",
                        transform=ax.transAxes,
                        **bluebelt.config("distribution_plot.name"),
                    )

                if id == 0:
                    ax.set_title(title)
                ax.set_xticks([])
                ax.set_yticks([])

                ax.set_ylim(ax.get_xlim())

            else:
                ax.axis("off")

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


def _data_dict(frame):
    return {k: v.dropna().values for k, v in frame.items()}


def _get_h0_equal_means(columns):
    if len(columns) == 1:
        return ""
    elif len(columns) > 4:
        return f"$H_0: \\bar{{X}}_{{{columns[0]}}} = \\bar{{X}}_{{{columns[1]}}} = \\bar{{X}}_{{...}} = \\bar{{X}}_{{{columns[-1]}}}$"
    else:
        result = f"$H_0: \\bar{{X}}_{{{columns[0]}}}$"
        for col in columns[1:]:
            result += f"$ = \\bar{{X}}_{{{col}}}$"
        return result


def _get_distribution(dist=None):
    distributions = {
        "norm": "Normal (Gaussian)",
        "alpha": "Alpha",
        "anglit": "Anglit",
        "arcsine": "Arcsine",
        "beta": "Beta",
        "betaprime": "Beta Prime",
        "bradford": "Bradford",
        "burr": "Burr",
        "cauchy": "Cauchy",
        "chi": "Chi",
        "chi2": "Chi-squared",
        "cosine": "Cosine",
        "dgamma": "Double Gamma",
        "dweibull": "Double Weibull",
        "erlang": "Erlang",
        "expon": "Exponential",
        "exponweib": "Exponentiated Weibull",
        "exponpow": "Exponential Power",
        "fatiguelife": "Fatigue Life (Birnbaum-Sanders)",
        "foldcauchy": "Folded Cauchy",
        "f": "F (Snecdor F)",
        "fisk": "Fisk",
        "foldnorm": "Folded Normal",
        "frechet_r": "Frechet Right Sided, Extreme Value Type II",
        "frechet_l": "Frechet Left Sided, Weibull_max",
        "gamma": "Gamma",
        "gausshyper": "Gauss Hypergeometric",
        "genexpon": "Generalized Exponential",
        "genextreme": "Generalized Extreme Value",
        "gengamma": "Generalized gamma",
        "genlogistic": "Generalized Logistic",
        "genpareto": "Generalized Pareto",
        "genhalflogist": "Generalized Half Logistic",
        "gilbrat": "Gilbrat",
        "gompertz": "Gompertz (Truncated Gumbel)",
        "gumbel_l": "Left Sided Gumbel, etc.",
        "gumbel_r": "Right Sided Gumbel",
        "halfcauchy": "Half Cauchy",
        "halflogistic": "Half Logistic",
        "halfnorm": "Half Normal",
        "hypsecant": "Hyperbolic Secant",
        "invgamma": "Inverse Gamma",
        "invnorm": "Inverse Normal",
        "invweibull": "Inverse Weibull",
        "johnsonsb": "Johnson SB",
        "johnsonsu": "Johnson SU",
        "laplace": "Laplace",
        "logistic": "Logistic",
        "loggamma": "Log-Gamma",
        "loglaplace": "Log-Laplace (Log Double Exponential",
        "lognorm": "Log-Normal",
        "lomax": "Lomax (Pareto of the second kind)",
        "maxwell": "Maxwell",
        "mielke": "Mielke's Beta-Kappa",
        "nakagami": "Nakagami",
        "ncx2": "Non-central chi-squared",
        "ncf": "Non-central F",
        "nct": "Non-central Student's T",
        "pareto": "Pareto",
        "powerlaw": "Power-function",
        "powerlognorm": "Power log normal",
        "powernorm": "Power normal",
        "rdist": "R distribution",
        "reciprocal": "Reciprocal",
        "rayleigh": "Rayleigh",
        "rice": "Rice",
        "recipinvgauss": "Reciprocal Inverse Gaussian",
        "semicircular": "Semicircular",
        "t": "Student's T",
        "triang": "Triangular",
        "truncexpon": "Truncated Exponential",
        "truncnorm": "Truncated Normal",
        "tukeylambda": "Tukey-Lambda",
        "uniform": "Uniform",
        "vonmises": "Von-Mises (Circular)",
        "wald": "Wald",
        "weibull_min": "Minimum Weibull (see Frechet)",
        "weibull_max": "Maximum Weibull (see Frechet)",
        "wrapcauchy": "Wrapped Cauchy",
        "ksone": "Kolmogorov-Smirnov one-sided (no st",
        "kstwobign": "Kolmogorov-Smirnov two-sided test for Large N",
    }

    return distributions.get(dist, None)
