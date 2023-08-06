import numpy as np
import pandas as pd
import bluebelt.analysis.datetime
import bluebelt.data.projection


def pattern(cls):
    def project(self, year=None, adjust_holidays=True):

        self._obj = bluebelt.data.projection.project(
            self._obj, year=year, adjust_holidays=adjust_holidays
        )
        self.pattern = bluebelt.data.projection.project(
            self.pattern, year=year, adjust_holidays=adjust_holidays
        )
        self.residuals = bluebelt.data.projection.project(
            self.residuals, year=year, adjust_holidays=adjust_holidays
        )
        self.outliers = bluebelt.data.projection.project(
            self.outliers, year=year, adjust_holidays=adjust_holidays
        )
        self.adjusted = bluebelt.data.projection.project(
            self.adjusted, year=year, adjust_holidays=adjust_holidays
        )
        self.upper = bluebelt.data.projection.project(
            self.upper, year=year, adjust_holidays=adjust_holidays
        )
        self.lower = bluebelt.data.projection.project(
            self.lower, year=year, adjust_holidays=adjust_holidays
        )
        self.out_of_bounds = bluebelt.data.projection.project(
            self.out_of_bounds, year=year, adjust_holidays=adjust_holidays
        )
        self.within_bounds = bluebelt.data.projection.project(
            self.within_bounds, year=year, adjust_holidays=adjust_holidays
        )

        return self

    def set_pattern(self, pattern=None):

        # quick fix for patterns that have more datapoints than self
        pattern = pattern[self._obj.index]

        if pattern.shape[0] < self._obj.shape[0]:
            raise ValueError(
                "The provided pattern does not match the original pattern. Please check the pattern index."
            )

        self.pattern = pattern
        self.shape = -1

        # replace the original observations
        self.set_observations()

        self.set_residuals()
        self.set_outliers()
        self.set_bounds()

        return self

    def add_weekday(self, values=None):
        values = values or self._obj
        weekday = bluebelt.analysis.datetime.WeekDay(values)

        # check if weekdays are relevamt
        if weekday.equal_means:
            raise ValueError("The weekdays have equal means.")

        self.pattern = (
            self.pattern * self.pattern.index.weekday.map(weekday.ratio).values
        )

        self.set_residuals()
        self.set_outliers()
        self.set_bounds()

        return self

    def add_monthday(self, values=None):
        values = values or self._obj
        monthday = bluebelt.analysis.datetime.MonthDay(values)

        # check if weekdays are relevamt
        if monthday.equal_means:
            raise ValueError("The monthdays have equal means.")

        self.pattern = (
            self.pattern * self.pattern.index.weekday.map(monthday.ratio).values
        )

        self.set_residuals()
        self.set_outliers()
        self.set_bounds()

        return self

    setattr(cls, "project", project)
    setattr(cls, "set_pattern", set_pattern)
    setattr(cls, "add_weekday", add_weekday)
    setattr(cls, "add_monthday", add_monthday)

    return cls
