# -*- coding: utf-8 -*-

import numpy as np
import warnings


# %%

def fill_series(x, year):
    """Returns the value of a timeseries (indexed over years) for a year
    by linear interpolation.

    Parameters
    ----------
    x: pandas.Series
        a timeseries to be interpolated
    year: int
        year of interpolation
    """
    x = x.dropna()
    if year in x.index and not np.isnan(x[year]):
        return x[year]
    else:
        prev = [i for i in x.index if i < year]
        nxt = [i for i in x.index if i > year]
        if prev and nxt:
            p = max(prev)
            n = min(nxt)
            return ((n - year) * x[p] + (year - p) * x[n]) / (n - p)
        else:
            return np.nan


def cumulative(x, first_year, last_year):
    """Returns the cumulative sum of a timeseries (indexed over years),
    implements linear interpolation between years, ignores nan's in the range.
    The function includes the last-year value of the series, and
    raises a warning if start_year or last_year is outside of
    the timeseries range and returns nan

    Parameters
    ----------
    x: pandas.Series
        a timeseries to be summed over time
    first_year: int
        first year of the sum
    last_year: int
        last year of the sum (inclusive)
    """

    if min(x.index) > first_year:
        # if the timeseries does not cover the range `[first_year, last_year]`,
        # replace by nan to avoid erroneous aggregation
        warnings.warn('timeseries {} does not start by {}'.format(x.name,
                      first_year))
        return np.nan

    if max(x.index) < last_year:
        warnings.warn('the timeseries {} does not extend until {}'
                      .format(x.name, last_year))
        return np.nan

    x[first_year] = fill_series(x, first_year)
    x[last_year] = fill_series(x, last_year)

    years = [i for i in x.index if i >= first_year and i <= last_year
             and ~np.isnan(x[i])]
    years.sort()

    # loop over years
    if not np.isnan(x[first_year]) and not np.isnan(x[last_year]):
        value = 0
        for (i, yr) in enumerate(years[:-1]):
            next_yr = years[i+1]
            # the summation is shifted to include the first year fully in sum,
            # otherwise, would return a weighted average of `yr` and `next_yr`
            value += ((next_yr - yr - 1) * x[next_yr] +
                      (next_yr - yr + 1) * x[yr]) / 2

        # the loop above does not include the last element in range
        # (`last_year`), therefore added explicitly
        value += x[last_year]

        return value
