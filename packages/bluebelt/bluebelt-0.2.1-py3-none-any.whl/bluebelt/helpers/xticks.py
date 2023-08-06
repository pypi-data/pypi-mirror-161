import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import matplotlib.dates as mdates

import bluebelt.styles.defaults

def set_xticks(ax=None, index=None, location=None, group=None):
    if isinstance(index, pd.MultiIndex):
        set_multiindex_xticks(ax=ax, index=index, group=group)
    elif isinstance(index, pd.DatetimeIndex):
        set_datetimeindex_xticks(ax=ax, index=index)
    else:
        ax.set_xticks(location)
        ax.set_xticklabels(index)

# datetimeindex
def set_datetimeindex_xticks(ax, index):
    '''
    set the xticks for a pandas DatetimeIndex
    '''

    rng = index.max() - index.min()
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

# multiindex
def set_multiindex_xticks(ax, index, levels=[0, 1], group=None):
    trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)

    # get the proper levels
    levels = _find_multiindex_levels(index=index, levels=levels)

    # hide the old ticks
    ax.tick_params(axis='x', length=0)

    # get ax size
    ax_size = ax.get_window_extent().transformed(ax.get_figure().dpi_scale_trans.inverted())
    
    for i, level in enumerate(levels):
        if i == 0:
            
            # calculate group size if not provided
            if not group:
                _group = (index.size/(ax_size.width*bluebelt.styles.defaults.small)) * 5.5
                if _group > 1:
                    _group *= 2
                _groups = np.array([1, 4, 13])
                group = _groups[np.greater_equal(_groups - _group, 0).argmax()]

            xticks, xticklabels, line_locations = _get_multiindex_xticks(index=index, level=level, group=group)

            # set real xticks
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticklabels)
            
            # draw lines between xticks
            ypos = 0.005
            length = 0.01
            for xpos in line_locations:
                _add_line(ax, xpos, ypos, length)
                
        else:
            xticks, xticklabels, line_locations = _get_multiindex_xticks(index=index, level=level, group=1)

            # get label position compared to ax height
            label_pos = -bluebelt.styles.defaults.small/(ax_size.height*35)

            # set extra xticks
            for tick, label in zip(xticks, xticklabels):
                ax.text(tick, label_pos, label, ha='center', transform=trans)
            
            # draw lines between xticks
            ypos = 0.005
            length = -label_pos
            for xpos in line_locations:
                _add_line(ax, xpos, ypos, length)

    
def _get_multiindex_xticks(index, level, group):
    
    codes = index.codes[level]
    
    # build values
    values = np.array([index.levels[level][code] for code in codes])
    label_values = values[np.where(np.append(values[:-1] != values[1:], True))[0]]
    values = (np.ceil((values / group) - 1) * group) + 1
    
    
    sub_values = np.concatenate(([0,], (np.where(values[:-1] != values[1:])[0]) + 1, [len(values)]))

    # get interval medians
    median_func = lambda x: (x-1)/2
    intervals = sub_values[1:]-sub_values[:-1]
    intervals = median_func(intervals)

    # get new xticks
    xticks = intervals + sub_values[:-1]

    # make new labels
    label_values_grouped = (np.ceil((label_values / group) - 1) * group) + 1
    index_min = np.concatenate(([0,], (np.where(label_values_grouped[:-1] != label_values_grouped[1:])[0]) + 1))
    index_max = np.concatenate((np.where(label_values_grouped[:-1] != label_values_grouped[1:])[0], [len(label_values_grouped) - 1]))
    s1 = np.maximum(np.array([label_values[i] for i in index_min]), np.array([label_values_grouped[i] for i in index_min])).astype(int)
    s2 = np.array([label_values[i] for i in index_max]).astype(int)
    if group > 1:
        # check if the last tick value is in s1 or s2
        if not label_values[-1] in np.concatenate((s1, s2), 0):
            s2 = np.append(s2, label_values[-1])
        xticklabels = [f'{s1[i]}-{s2[i]}' if (s1[i]!=s2[i] and i < len(s2)) else f'{s1[i]}' for i in range(len(s1))]
    else:
        xticklabels = label_values

    # calculate location of lines
    line_locations = np.concatenate(([1,], np.diff(values, n=1)[:-1])).nonzero()[0]
    line_locations = (np.concatenate((line_locations, [index.shape[0]])))
    line_locations = line_locations - 0.5
    
    return xticks, xticklabels, line_locations

def _find_multiindex_levels(index, levels, final_assembly=True):
    names = index.names
    if isinstance(levels, str):
        levels = names.index(levels)
    elif isinstance(levels, int):
        levels = levels
    elif isinstance(levels, (list, tuple)):
        levels = sorted([_find_multiindex_levels(index=index, levels=level, final_assembly=False) for level in levels], reverse=True)
    
    # make the levels a list if 
    if final_assembly and not isinstance(levels, list):
        levels = [levels]
    return levels

def _add_line(ax, xpos, ypos, length):
    trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
    line = plt.Line2D([xpos, xpos], [ypos - length, ypos], color='black', transform=trans)
    line.set_clip_on(False)
    ax.add_line(line)

             