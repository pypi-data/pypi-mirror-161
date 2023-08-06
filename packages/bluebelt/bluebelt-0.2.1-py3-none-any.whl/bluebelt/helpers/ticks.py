import datetime
import numpy as np

import matplotlib.ticker
import matplotlib.dates

def ticks(_obj, ax, **kwargs):

    max_xticks = kwargs.get('max_xticks', get_max_xticks(ax))
    #ax.minorticks_off()

    # set year ticks at major positions
    ticks = _obj.index.unique()
    step = int(np.ceil(len(ticks)/np.minimum(len(ticks), max_xticks)))
    ticklabels = ticks[::step]
    locator_major = matplotlib.ticker.FixedLocator(range(1, len(ticks)+1, step))
    ax.xaxis.set_major_locator(locator_major)
    ax.set_xticklabels(ticklabels)
    
def week(_obj, ax, **kwargs):

    max_xticks = kwargs.get('max_xticks', get_max_xticks(ax))
        
    # set year ticks at major positions
    year_ticks = []#get_year_ticks(_obj, max_xticks=max_xticks)
    locator_major = matplotlib.ticker.FixedLocator(year_ticks)
    formatter_major = matplotlib.dates.DateFormatter('%V\n%G')
    ax.xaxis.set_major_locator(locator_major)
    ax.xaxis.set_major_formatter(formatter_major)

    # set week ticks at minor positions
    week_ticks = get_week_ticks(_obj, max_xticks=max_xticks)
    locator_minor = matplotlib.ticker.FixedLocator(week_ticks)
    formatter_minor = matplotlib.dates.DateFormatter('%V')
    ax.xaxis.set_minor_locator(locator_minor)
    ax.xaxis.set_minor_formatter(formatter_minor)

def year_week(_obj, ax, **kwargs):

    max_xticks = kwargs.get('max_xticks', get_max_xticks(ax))

    # set year ticks at major positions
    year_ticks = get_year_ticks(_obj, max_xticks=max_xticks)
    locator_major = matplotlib.ticker.FixedLocator(year_ticks)
    formatter_major = matplotlib.dates.DateFormatter('%V\n%G')
    ax.xaxis.set_major_locator(locator_major)
    ax.xaxis.set_major_formatter(formatter_major)

    # set week ticks at minor positions
    week_ticks = get_week_ticks(_obj, max_xticks=max_xticks)
    locator_minor = matplotlib.ticker.FixedLocator(week_ticks)
    formatter_minor = matplotlib.dates.DateFormatter('%V')
    ax.xaxis.set_minor_locator(locator_minor)
    ax.xaxis.set_minor_formatter(formatter_minor)


def get_year_ticks(obj, max_xticks=17):
    
    if max_xticks is not None:
        rng = obj.index.isocalendar().year.unique().size
        _group = np.ceil(rng/max_xticks)
        _groups = np.array([1, 4, 13, 26, 52])
        group = _groups[np.greater_equal(_groups - _group, 0).argmax()]
    else:
        group = 1
        
    ticks = []
    years = obj.index.isocalendar().year.unique()
    if group > 1:
        years = years[np.where(np.mod(years, group)==1)]
        
    for year in years:#obj.index.isocalendar().year.unique():
        ticks.append(matplotlib.dates.date2num(datetime.datetime.fromisocalendar(year, 1, 1)))
            
    return ticks

def get_week_ticks(obj, max_xticks=17):
    
    if max_xticks is not None:
        rng = obj.index.isocalendar()[['year', 'week']].apply(tuple, axis=1).unique().size
        _group = np.ceil(rng/max_xticks)
        _groups = np.array([1, 4, 13, 26, 52])
        group = _groups[np.greater_equal(_groups - _group, 0).argmax()]
    else:
        group = 1
    
    ticks = []
    for year in obj.index.isocalendar().year.unique():
        weeks = obj[obj.index.isocalendar().year==year].index.isocalendar().week.unique().to_numpy()
        if group > 1:
            weeks = weeks[np.where(np.mod(weeks, group)==1)]
        for week in weeks:
            if week < 53: # that would mess things up
                ticks.append(matplotlib.dates.date2num(datetime.datetime.fromisocalendar(year, week, 1)))
            
    return ticks

def get_max_xticks(ax, ratio=0.75):
    
    # get ax width in pixels
    ax_width = ax.figure.get_figwidth() * (ax.figure.subplotpars.right - ax.figure.subplotpars.left) * ax.figure.dpi
    
    # get text width: tick label font size * 2 characters * .75 width ratio
    label_width = ax.xaxis.get_majorticklabels()[0].get_fontsize() * 2 * ratio
    
    return np.floor(ax_width / label_width)