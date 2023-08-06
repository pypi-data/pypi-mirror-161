import os

import bluebelt
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

import bluebelt.helpers.ticks

import warnings

def _get_frame(_obj, **kwargs):

    columns = kwargs.get('columns', None)

    if isinstance(_obj, pd.DataFrame) and isinstance(columns, (str, list)):
        return _obj[columns]
    elif isinstance(_obj, pd.Series):
        return pd.DataFrame(_obj)
    else:
        return _obj

def _get_name(_obj, **kwargs):

    if isinstance(_obj, pd.Series):
        return _obj.name
    elif isinstance(_obj, pd.DataFrame):
        names = []
        for col in _obj.columns:
            names.append(col)
        return bluebelt.core.helpers._get_nice_list(names)
    else:
        return None

def line(_obj, xlim=(None, None), ylim=(None, None), max_xticks=None, format_xticks=None, format_yticks=None, title=None, xlabel=None, ylabel=None, legend=True, path=None, **kwargs):
    frame = _get_frame(_obj, **kwargs)

    # prepare figure
    fig, ax = plt.subplots(nrows=1, ncols=1, **kwargs)

    for id, col in enumerate(frame):
        ax.plot(frame[col].index, frame[col].values, **bluebelt.config(f"line{id%6}"), label=col)
        
    # limit axis
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    # set ticks
    if max_xticks is None:
        max_xticks = bluebelt.helpers.ticks.get_max_xticks(ax)
    bluebelt.helpers.ticks.year_week(frame, ax=ax, max_xticks=max_xticks)

    # format ticks
    if format_xticks:
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels([f'{x:{format_xticks}}' for x in ax.get_xticks()])
    if format_yticks:
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels([f'{y:{format_yticks}}' for y in ax.get_yticks()])

    # labels
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    # legend
    if legend:
        ax.legend()
    elif ax.get_legend() is not None:
        ax.get_legend().set_visible(False)
    
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

def area(_obj, xlim=(None, None), ylim=(None, None), max_xticks=None, format_xticks=None, format_yticks=None, title=None, xlabel=None, ylabel=None, legend=True, path=None, **kwargs):
    frame = _get_frame(_obj, **kwargs)

    # prepare figure
    fig, ax = plt.subplots(nrows=1, ncols=1, **kwargs)

    for id, col in enumerate(frame):
        ax.fill_between(frame[col].index, frame[col].values, **bluebelt.config(f"fill{id%6}"))
        ax.plot(frame[col].index, frame[col].values, **bluebelt.config(f"line{id%6}"), label=col)
        
    # limit axis
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    # set ticks
    if max_xticks is None:
        max_xticks = bluebelt.helpers.ticks.get_max_xticks(ax)
    bluebelt.helpers.ticks.year_week(frame, ax=ax, max_xticks=max_xticks)

    # format ticks
    if format_xticks:
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels([f'{x:{format_xticks}}' for x in ax.get_xticks()])
    if format_yticks:
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels([f'{y:{format_yticks}}' for y in ax.get_yticks()])

    # labels
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    # legend
    if legend:
        ax.legend()
    elif ax.get_legend() is not None:
        ax.get_legend().set_visible(False)
    
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

def hist(_obj, bins=20, xlim=(None, None), ylim=(None, None), format_xticks=None, format_yticks=None, title=None, xlabel=None, ylabel=None, legend=True, path=None, **kwargs):
    frame = _get_frame(_obj, **kwargs)

    # prepare figure
    fig, ax = plt.subplots(nrows=1, ncols=1, **kwargs)

    bins = (np.nanmax(frame.to_numpy())-np.nanmin(frame.to_numpy()))/bins
    bins = np.arange(np.nanmin(frame), np.nanmax(frame)+bins, bins)

    for id, col in enumerate(frame):
        ax.hist(frame[col], bins=bins, label=col, **bluebelt.config(f"hist{id%6}"))
        
    # limit axis
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    # format ticks
    if format_xticks:
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels([f'{x:{format_xticks}}' for x in ax.get_xticks()])
    if format_yticks:
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels([f'{y:{format_yticks}}' for y in ax.get_yticks()])

    # labels
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    # legend
    if legend:
        ax.legend()
    elif ax.get_legend() is not None:
        ax.get_legend().set_visible(False)
    
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

def box(_obj, xlim=(None, None), ylim=(None, None), format_xticks=None, format_yticks=None, title=None, xlabel=None, ylabel=None, path=None, **kwargs):
    frame = _get_frame(_obj, **kwargs)
    labels = frame.columns

    # drop na values
    frame = [series.dropna().to_list() for name, series in frame.iteritems()]

    # prepare figure
    fig, ax = plt.subplots(nrows=1, ncols=1, **kwargs)

    boxplot = ax.boxplot(frame, labels=labels, **kwargs)

    for box in boxplot['boxes']:
        box.set(**bluebelt.config('boxplot.boxes'))
        
    # limit axis
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    # format ticks
    if format_xticks:
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels([f'{x:{format_xticks}}' for x in ax.get_xticks()])
    if format_yticks:
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels([f'{y:{format_yticks}}' for y in ax.get_yticks()])

    # labels
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

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

def waterfall(series, horizontal=False, invertx=False, inverty=False, width=0.6, height=0.6, xlim=(None, None), ylim=(None, None), format_xticks=None, format_yticks=None, title=None, xlabel=None, ylabel=None, path=None, **kwargs):

    title = title or f"{_get_name(series)} waterfall"

    if not isinstance(series, pd.Series):
        raise ValueError('Waterfall charts need a pandas.Series')
    
    measure = pd.Series(kwargs.pop('measure', ['relative'] * series.shape[0]))

    # are the totals ok?
    if ('total' in measure.unique()) and not (series.where((measure=='relative').values).cumsum().shift().where((measure=='total').values).fillna(0) == series.where((measure=='total').values).fillna(0)).all():
        warnings.warn('The totals values are not the totals of the preceeding values. This will be adjusted.', Warning)
        series = series.where((measure=='relative').values).cumsum().shift().where((measure=='total').values, series).fillna(0)

    # calculations
    bottom = series.where((measure=='relative').values).fillna(0).cumsum() - series
    index = np.arange(series.index.shape[0])

    ylim = ylim or ((bottom).min() * 1.05, (series+bottom).max() * 1.05)
    xlim = xlim or ((bottom).min() * 1.05, (series+bottom).max() * 1.05)
    
    fig, ax = plt.subplots(nrows=1, ncols=1)
    
    if horizontal:
        
        # totals
        ax.barh(index, series.where((measure=='total').values).values, left=bottom, height=height, **bluebelt.config('waterfall.total'))
        ax.barh(index, series.where((measure=='total').values).values, left=bottom, height=height, **bluebelt.config('waterfall.border'))

        # increasing
        ax.barh(index, series.where((series>=0) & ((measure=='relative').values)).values, left=bottom, height=height, **bluebelt.config('waterfall.increasing'))
        ax.barh(index, series.where((series>=0) & ((measure=='relative').values)).values, left=bottom, height=height, **bluebelt.config('waterfall.border'))

        # decreasing
        ax.barh(index, series.where((series<0) & ((measure=='relative').values)).values, left=bottom, height=height, **bluebelt.config('waterfall.decreasing'))
        ax.barh(index, series.where((series<0) & ((measure=='relative').values)).values, left=bottom, height=height, **bluebelt.config('waterfall.border'))

        # connectors
        ax.vlines(x=(bottom + series)[:-1], ymin=(index)[:-1], ymax=(index+0.5)[:-1]+(1-height), **bluebelt.config('waterfall.connectors'))

        # yticks
        ax.set_yticks(index)
        ax.set_yticklabels(series.index.values)
        
        # swap margins
        xmargin, ymargin = ax.margins()        
        ax.set_xmargin(ymargin)
        ax.set_ymargin(xmargin)

    else:
        # totals
        ax.bar(index, series.where((measure=='total').values).values, bottom=bottom, width=width, **bluebelt.config('waterfall.total'))
        ax.bar(index, series.where((measure=='total').values).values, bottom=bottom, width=width, **bluebelt.config('waterfall.border'))

        # increasing
        ax.bar(index, series.where((series>=0) & ((measure=='relative').values)).values, bottom=bottom, width=width, **bluebelt.config('waterfall.increasing'))
        ax.bar(index, series.where((series>=0) & ((measure=='relative').values)).values, bottom=bottom, width=width, **bluebelt.config('waterfall.border'))

        # decreasing
        ax.bar(index, series.where((series<0) & ((measure=='relative').values)).values, bottom=bottom, width=width, **bluebelt.config('waterfall.decreasing'))
        ax.bar(index, series.where((series<0) & ((measure=='relative').values)).values, bottom=bottom, width=width, **bluebelt.config('waterfall.border'))

        # connectors
        ax.hlines(y=(bottom + series)[:-1], xmin=(index)[:-1], xmax=(index+0.5)[:-1]+(1-height), **bluebelt.config('waterfall.connectors'))

        # xticks
        ax.set_xticks(index)
        ax.set_xticklabels(series.index.values)
        
    # limit axis
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    # invert axis
    if invertx:
        ax.invert_xaxis()
    if inverty:
        ax.invert_yaxis()
    
    # format ticks
    if format_xticks:
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels([f'{x:{format_xticks}}' for x in ax.get_xticks()])
    if format_yticks:
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels([f'{y:{format_yticks}}' for y in ax.get_yticks()])

    # labels
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    
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
    
