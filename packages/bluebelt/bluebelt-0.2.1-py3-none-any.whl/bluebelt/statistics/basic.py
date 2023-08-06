import os

import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

import bluebelt.helpers.text


class Correlation:
    def __init__(self, frame, columns=None, confidence=0.95, **kwargs):

        # check arguments
        if not isinstance(frame, pd.DataFrame):
            raise ValueError("frame is not a Pandas DataFrame")

        if columns is not None and not isinstance(columns, list):
            raise ValueError("columns is not a list")

        self.frame = frame if columns is None else frame[columns]
        self.columns = columns if columns is not None else self.frame.columns.to_list()
        self.nrows = self.frame.shape[0]
        self.ncols = self.frame.shape[1]
        self.confidence = confidence

        self.calculate()

    def calculate(self):
        self.z = stats.norm.ppf(1 - (1 - self.confidence) / 2)
        self.rci = self._r_ci()

    def __str__(self):
        precision = 3

        result = f"Pearson correlation coefficient with {self.confidence*100:1.1f}% confidence interval\n\n"
        result += (
            self._r_ci()
            .applymap(
                lambda x: np.round(x, precision)
                if isinstance(x, (np.floating, int, float, tuple))
                else x
            )
            .to_string()
        )

        return result

    def __repr__(self):
        return f"{self.__class__.__name__}(columns={self.columns}, nrows={self.nrows}, ncols={self.ncols}, confidence={self.confidence})"

    @property
    def result(self, precision=3):
        print(
            self._r_ci()
            .applymap(
                lambda x: np.round(x, precision)
                if isinstance(x, (np.floating, int, float, tuple))
                else x
            )
            .to_string()
        )

    def plot(self, format_stats="1.2f", title=None, path=None, **kwargs):

        title = (
            title
            or f"correlation plot for {bluebelt.helpers.text._get_nice_list(self.columns)}"
        )

        fig, ax = plt.subplots(nrows=self.ncols, ncols=self.ncols, **kwargs)
        for row, row_name in enumerate(self.columns):
            for col, col_name in enumerate(self.columns):
                if row == col:
                    # plot a histogram where row and column are equal
                    ax[row, col].hist(
                        self.frame[row_name], **bluebelt.config("correlation.hist")
                    )
                else:
                    # plot a scatter plot
                    ax[row, col].plot(
                        self.frame[col_name],
                        self.frame[row_name],
                        **bluebelt.config("correlation.plot"),
                    )

                    # plot regression line
                    dfx = self.frame[
                        self.frame[col_name].notna() & self.frame[row_name].notna()
                    ]
                    a, b = np.polyfit(dfx[col_name], dfx[row_name], 1)
                    ax[row, col].plot(
                        dfx[col_name],
                        (a * dfx[col_name] + b),
                        **bluebelt.config("correlation.line"),
                    )

                    # fetch r and ci
                    r_value = self.rci.iloc[row, col * 2]
                    rho_l = self.rci.iloc[row, 1 + col * 2][0]
                    rho_u = self.rci.iloc[row, 1 + col * 2][1]
                    ax[row, col].text(
                        0.02,
                        0.98,
                        f"r :{r_value:{format_stats}} CI: ({rho_l:{format_stats}} - {rho_u:{format_stats}})",
                        transform=ax[row, col].transAxes,
                        **bluebelt.config("correlation.text"),
                    )

                    # share X-axis
                    if col == 0 and row > 1:
                        ax[row, col].sharex(ax[1, col])
                    elif col > 0 and row > 0:
                        ax[row, col].sharex(ax[0, col])

                    # share Y-axis
                    if row == 0 and col > 1:
                        ax[row, col].sharey(ax[row, 1])
                    elif row > 0 and col > 0:
                        ax[row, col].sharey(ax[row, 0])

                if row == self.ncols - 1:
                    ax[row, col].set_xlabel(col_name)

                if col == 0:
                    ax[row, col].set_ylabel(row_name)

                ax[row, col].set_xticks([])
                ax[row, col].set_yticks([])

        # labels
        if title:
            ax[0, 0].set_title(title)

        plt.tight_layout()
        plt.subplots_adjust(hspace=0)
        plt.subplots_adjust(wspace=0)

        # file
        if path:
            if len(os.path.dirname(path)) > 0 and not os.path.exists(
                os.path.dirname(path)
            ):
                os.makedirs(os.path.dirname(path))
            plt.savefig(path)
            plt.close()
        else:
            plt.close()
            return fig

    def _r_ci(self):

        cols = []
        for col in range(0, self.ncols):
            rows = []
            for row in range(0, self.ncols):

                # calculate r and ci
                if row != col:
                    frame = self.frame[[self.columns[row], self.columns[col]]].dropna(
                        axis=0
                    )

                    r_value = np.corrcoef(
                        frame[self.columns[row]], frame[self.columns[col]]
                    )[0, 1]
                    z_l = 0.5 * (np.log(1 + r_value) - np.log(1 - r_value)) - self.z / (
                        frame.shape[0] - 3
                    )
                    z_u = 0.5 * (np.log(1 + r_value) - np.log(1 - r_value)) + self.z / (
                        frame.shape[0] - 3
                    )
                    rho_l = (np.exp(2 * z_l) - 1) / (np.exp(2 * z_l) + 1)
                    rho_u = (np.exp(2 * z_u) - 1) / (np.exp(2 * z_u) + 1)

                    ci = [r_value, (rho_l, rho_u)]
                else:
                    ci = ["", ""]  # [1., 1., 1.]

                rows += ci
            cols.append(rows)

        columns_array = np.array(
            [
                item
                for sublist in [[col] * 2 for col in self.frame.columns]
                for item in sublist
            ]
            + ["r", "CI"] * self.ncols
        ).reshape(2, self.ncols * 2)
        columns = pd.MultiIndex.from_tuples(
            list(zip(*columns_array))
        )  # , names=["array", "value"])

        return pd.DataFrame(cols, index=self.columns, columns=columns)

    def _ci(self):

        cols = []
        for col in range(0, self.ncols):
            rows = []
            for row in range(0, self.ncols):

                # calculate r and ci
                if row != col:
                    frame = self.frame[[self.columns[row], self.columns[col]]].dropna(
                        axis=0
                    )

                    r_value = np.corrcoef(
                        frame[self.columns[row]], frame[self.columns[col]]
                    )[0, 1]
                    z_l = 0.5 * (np.log(1 + r_value) - np.log(1 - r_value)) - self.z / (
                        frame.shape[0] - 3
                    )
                    z_u = 0.5 * (np.log(1 + r_value) - np.log(1 - r_value)) + self.z / (
                        frame.shape[0] - 3
                    )
                    rho_l = (np.exp(2 * z_l) - 1) / (np.exp(2 * z_l) + 1)
                    rho_u = (np.exp(2 * z_u) - 1) / (np.exp(2 * z_u) + 1)

                    ci = (rho_l, rho_u)
                else:
                    ci = (1.0, 1.0)

                rows.append(ci)
            cols.append(rows)

        return pd.DataFrame(cols, index=self.columns, columns=self.columns)

    def _r(self):
        return pd.DataFrame(
            [
                [
                    (np.corrcoef(self.frame[col], self.frame[row])[0, 1])
                    for col in self.columns
                ]
                for row in self.columns
            ],
            index=self.columns,
            columns=self.columns,
        )
