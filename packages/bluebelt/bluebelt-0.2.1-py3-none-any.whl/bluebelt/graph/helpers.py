import re
import math
from decimal import Decimal

import numpy as np
import pandas as pd
from scipy.stats import distributions

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from itertools import groupby

# matplotlib format
def _axisformat(ax, series):

    if isinstance(series.index, pd.DatetimeIndex):
        rng = series.index.max() - series.index.min()

        if rng > pd.Timedelta('365 days'):
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
            ax.set_xlabel('month')
        elif rng > pd.Timedelta('183 days'):
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.set_xlabel('month')
        elif rng > pd.Timedelta('31 days'):
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%V'))
            ax.set_xlabel('week')
        else:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
            ax.set_xlabel('date')
    elif isinstance(series, pd.DataFrame):
        ax.set_xlabel(series.iloc[:,0].name)
        ax.set_ylabel(series.index.name)
    else:
        ax.set_xlabel(series.name)

    return ax

import matplotlib.transforms as transforms

def _get_multiindex_xticks(index, level, factor):
    
    codes = index.codes[level]
    
    # build values
    values = np.array([index.levels[level][code] for code in codes])
    label_values = values[np.where(np.append(values[:-1] != values[1:], True))[0]]
    values = (np.ceil((values / factor) - 1) * factor) + 1
    
    
    sub_values = np.concatenate(([0,], (np.where(values[:-1] != values[1:])[0]) + 1, [len(values)]))

    # get interval medians
    median_func = lambda x: (x-1)/2
    intervals = sub_values[1:]-sub_values[:-1]
    intervals = median_func(intervals)

    # get new xticks
    xticks = intervals + sub_values[:-1]

    # make new labels
    label_values_grouped = (np.ceil((label_values / factor) - 1) * factor) + 1
    index_min = np.concatenate(([0,], (np.where(label_values_grouped[:-1] != label_values_grouped[1:])[0]) + 1))
    index_max = np.concatenate((np.where(label_values_grouped[:-1] != label_values_grouped[1:])[0], [len(label_values_grouped) - 1]))
    s1 = np.maximum(np.array([label_values[i] for i in index_min]), np.array([label_values_grouped[i] for i in index_min])).astype(int)
    s2 = np.array([label_values[i] for i in index_max]).astype(int)
    if factor > 1:
        # check if the last tick value is in s1 or s2
        if not label_values[-1] in np.concatenate((s1, s2), 0):
            s2 = np.append(s2, label_values[-1])
        xticklabels = [f'{s1[i]}-{s2[i]}' if (s1[i]!=s2[i] and i < len(s2)) else f'{s1[i]}' for i in range(len(s1))]
    else:
        xticklabels = label_values

    # calculate location of lines
    line_locations = np.concatenate(([1,], np.diff(values, n=1)[:-1])).nonzero()[0]
    line_locations = (np.concatenate((line_locations, [s.shape[0]])))
    line_locations = line_locations - 0.5
    
    return xticks, xticklabels, line_locations

def _find_multiindex_levels(index, levels):
    names = index.names
    if isinstance(levels, str):
        levels = names.index(levels)
    elif isinstance(levels, int):
        levels = levels
    elif isinstance(levels, (list, tuple)):
        levels = sorted([_find_index_levels(index=index, levels=level) for level in levels], reverse=True)
        
    if not isinstance(levels, list):
        levels = [levels]
    return levels

def _add_line(ax, xpos, ypos, length, style):
    trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
    line = plt.Line2D([xpos, xpos], [ypos - length, ypos], transform=trans, **style.graphs.line.multiindex_label_line)
    line.set_clip_on(False)
    ax.add_line(line)
    
def set_multiindex_xticks(ax, index, levels=[0, 1], factor=1, **kwargs):
    style = kwargs.pop('style', {'color': 'black'})

    trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
    # get the proper levels
    levels = _find_multiindex_levels(index=index, levels=levels)
    
    # hide the old ticks
    ax.tick_params(axis='x', length=0)
    
    for i, level in enumerate(levels):
        if i == 0:
            xticks, xticklabels, line_locations = _get_multiindex_xticks(index=index, level=level, factor=factor)
            
            # set real xticks
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticklabels)
            
            # draw lines between xticks
            ypos = 0.005
            length = 0.01
            for xpos in line_locations:
                _add_line(ax, xpos, ypos, length, style)
                
        else:
            xticks, xticklabels, line_locations = _get_multiindex_xticks(index=index, level=level, factor=1)
            
            label_pos = -0.08
            # set extra xticks
            for tick, label in zip(xticks, xticklabels):
                ax.text(tick, label_pos, label, ha='center', transform=trans)
            
            # draw lines between xticks
            ypos = 0.005
            length = 0.08
            for xpos in line_locations:
                _add_line(ax, xpos, ypos, length, style)
             
def _get_multiindex_labels(ax, _obj, style):
    # great thanks to Trenton McKinney
    # https://stackoverflow.com/questions/19184484/how-to-add-group-labels-for-bar-charts-in-matplotlib

    def _add_line(ax, xpos, ypos):
        line = plt.Line2D([xpos, xpos], [ypos + .025, ypos], transform=ax.transAxes, **style.graphs.line.multiindex_label_line)
        line.set_clip_on(False)
        ax.add_line(line)

    def _get_label_len(my_index,level):
        labels = my_index.get_level_values(level)
        return [(k, sum(1 for i in g)) for k,g in groupby(labels)]

    # remove current labels
    ax.set_xticklabels([])
    ax.set_xlabel('')

    # draw new labels
    ypos = -.025
    
    # margins
    xmargins = 2 * ax.margins()[0]

    scale = (1.-xmargins)/(_obj.index.size - 1)
    for level in range(_obj.index.nlevels)[::-1]:
        pos = 0
        for label, rpos in _get_label_len(_obj.index,level):
            #lxpos = ((pos + .5 * rpos)*scale) + ax.margins()[0]
            #ax.text(lxpos, ypos, label, ha='center', transform=ax.transAxes)
            _add_line(ax, (pos*scale) + ax.margins()[0], ypos)
            pos += rpos
        #_add_line(ax, (pos*scale) + ax.margins()[0] , ypos)
        ypos -= .1


def _get_multiindex_labels_old(ax, _obj, style):
    # great thanks to Trenton McKinney
    # https://stackoverflow.com/questions/19184484/how-to-add-group-labels-for-bar-charts-in-matplotlib

    def _add_line(ax, xpos, ypos):
        line = plt.Line2D([xpos, xpos], [ypos + .1, ypos], transform=ax.transAxes, **style.graphs.line.multiindex_label_line)
        line.set_clip_on(False)
        ax.add_line(line)

    def _get_label_len(my_index,level):
        labels = my_index.get_level_values(level)
        return [(k, sum(1 for i in g)) for k,g in groupby(labels)]

    # remove current labels
    ax.set_xticklabels([])
    ax.set_xlabel('')

    # draw new labels
    ypos = -.1
    #
    #
    #
    #
    scale = (1.-(2 * ax.margins()[0]))/_obj.index.size
    #scale = 1./_obj.index.size
    for level in range(_obj.index.nlevels)[::-1]:
        #
        #
        #
        pos = 0
        #
        #
        #
        # pos = 0
        for label, rpos in _get_label_len(_obj.index,level):
            lxpos = ((pos + .5 * rpos)*scale) + ax.margins()[0]
            ax.text(lxpos, ypos, label, ha='center', transform=ax.transAxes)
            _add_line(ax, (pos*scale) + ax.margins()[0], ypos)
            pos += rpos
        _add_line(ax, (pos*scale) + ax.margins()[0] , ypos)
        ypos -= .1


def _set_x_axis(ax, _obj):
    # set the x axis, depending on the index data type


    # xticks
    # if isinstance(_obj.series.index, pd.MultiIndex):
    #     bluebelt.graph.helpers._get_multiindex_labels(ax1, _obj.series, style)
    #     fig.subplots_adjust(bottom=.1*_obj.series.index.nlevels)
    # elif isinstance(_obj.series.index, pd.DatetimeIndex):
    #     bluebelt.graph.helpers._axisformat(ax1, _obj.series)
    
    
    #bluebelt.graph.helpers._axisformat(ax1, _obj.series)


    return 