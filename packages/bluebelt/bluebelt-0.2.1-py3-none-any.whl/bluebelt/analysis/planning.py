import os
import bluebelt
import pandas as pd

import bluebelt.helpers.ticks
import bluebelt.data.resolution
import matplotlib.pyplot as plt

from bluebelt.helpers.decorators.performance import performance

# to do
# -----
# add line plot for volume % per weekday per week
# add line plot for skill volume % per week and/or date

@performance
class Effort():
    def __init__(self, _obj, skip_na=True, skip_zero=True):  
        self._obj = _obj
        self.quantity = bluebelt.data.resolution.Resample(self._obj, 7).diff_quantity(skip_na=skip_na, skip_zero=skip_zero)
        self.distribution = bluebelt.data.resolution.Resample(self._obj, 7).diff_distribution(skip_na=skip_na, skip_zero=skip_zero)
        self.skills = bluebelt.data.resolution.Resample(self._obj, 7).diff_skills(skip_na=skip_na, skip_zero=skip_zero)
        self.qds = 1 - ((1 - self.quantity) * (1 - self.distribution) * (1 - self.skills))

    def __repr__(self):
        return (f'{self.__class__.__name__}(n={self._obj.shape[0]:1.0f}, qds={self.qds.mean():1.4f}, quantity={self.quantity.mean():1.4f}, distribution={self.distribution.mean():1.4f}, skills={self.skills.mean():1.4f})')
    
    def plot(self, xlim=(None, None), ylim=(0, 1), max_xticks=None, format_xticks=None, format_yticks=".0%", title=None, xlabel=None, ylabel=None, legend=True, path=None, **kwargs):
       
        # prepare figure
        fig, ax = plt.subplots(nrows=1, ncols=1, **kwargs)

        # q
        ax.fill_between(self.quantity.index[1:], 0, self.quantity.values[1:], label=f'quantity ({self.quantity.mean()*100:1.1f}%)', **bluebelt.config('effort.quantity.fill'))
        ax.plot(self.quantity.index[1:], self.quantity.values[1:], **bluebelt.config('effort.quantity.line'))
        
        # d
        ax.fill_between(self.distribution.index[1:], 0, self.distribution.values[1:], label=f'distribution ({self.distribution.mean()*100:1.1f}%)', **bluebelt.config('effort.distribution.fill'))
        ax.plot(self.distribution.index[1:], self.distribution.values[1:], **bluebelt.config('effort.distribution.line'))

        # s
        ax.fill_between(self.skills.index[1:], 0, self.skills.values[1:], label=f'skills ({self.skills.mean()*100:1.1f}%)', **bluebelt.config('effort.skills.fill'))
        ax.plot(self.skills.index[1:], self.skills.values[1:], **bluebelt.config('effort.skills.line'))
        
        # qds
        ax.plot(self.qds.index[1:], self.qds.values[1:], label=f'qds effort ({self.qds.mean()*100:1.1f}%)', **bluebelt.config('effort.qds.line'))
        
        # limit axis
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        
        # set xticks
        if max_xticks is None:
            max_xticks = bluebelt.helpers.ticks.get_max_xticks(ax)
        bluebelt.helpers.ticks.year_week(self.qds, ax=ax, max_xticks=max_xticks)

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

@performance
class Ease():
    def __init__(self, _obj, skip_na=True, skip_zero=True):
        self._obj = _obj
        self.quantity = 1 - bluebelt.data.resolution.Resample(self._obj, 7).diff_quantity(skip_na=skip_na, skip_zero=skip_zero)
        self.distribution = 1 - bluebelt.data.resolution.Resample(self._obj, 7).diff_distribution(skip_na=skip_na, skip_zero=skip_zero)
        self.skills = 1 - bluebelt.data.resolution.Resample(self._obj, 7).diff_skills(skip_na=skip_na, skip_zero=skip_zero)
        self.qds = self.quantity * self.distribution * self.skills

    def __repr__(self):
        return (f'{self.__class__.__name__}(n={self._obj.shape[0]:1.0f}, qds={self.qds.mean():1.4f}, quantity={self.quantity.mean():1.4f}, distribution={self.distribution.mean():1.4f}, skills={self.skills.mean():1.4f})')
    
    def plot(self, xlim=(None, None), width=0.8, format_yticks=".1%", title=None, xlabel=None, ylabel=None, path=None, **kwargs):
            
        title = title or f'planning QDS ease plot'
        
        # calculations
        qds = pd.Series({
            'q': self.quantity.mean(),
            'd': self.distribution.mean(),
            's': self.skills.mean(),
        }).reset_index(drop=True)

        vals = qds.cumprod()
        rest = (qds.cumprod().shift(1).fillna(1) - qds.cumprod())

        # prepare figure
        fig, ax = plt.subplots(nrows=1, ncols=1, **kwargs)

        # top
        ax.bar(rest.index, rest.values, bottom=vals.values, width=width, **bluebelt.config('ease.top.bar'))
        ax.bar(rest.index, rest.values, bottom=vals.values, width=width, **bluebelt.config('ease.borders.bar'))
        
        # bottom
        ax.bar(vals.index, vals.values, width=width, **bluebelt.config('ease.bottom.bar'))
        ax.bar(vals.index, vals.values, width=width, **bluebelt.config('ease.borders.bar'))
        
        
        # connectors
        xlim = ax.get_xlim()
        ax.bar((rest.index+0.5), 0, bottom=vals.values, width=1-width, **bluebelt.config('ease.connectors.bar'))
        
        ax.set_ylim(0,1.1)
        ax.set_xlim(xlim)
        ax.set_xticks([0,1,2])
        ax.set_xticklabels(['Q','D','S'])
        ax.tick_params(axis="x", bottom=True, top=False, labelbottom=True, labeltop=False)

        for tick in ax.get_xticks():
            ax.text(tick, vals.iloc[tick]+(rest.iloc[tick] / 2), f'{(1-qds.iloc[tick]):{format_yticks}}', **bluebelt.config('ease.values'))
            ax.text(tick, (vals.iloc[tick] / 2), f'{qds.iloc[tick]:{format_yticks}}', **bluebelt.config('ease.values'))
            
        # manage yticks
        yticks = [0, qds.cumprod().iloc[-1], 1]
        ax.set_yticks(yticks)
        ax.set_yticklabels([f'{y:{format_yticks}}' for y in ax.get_yticks()])
        ax.yaxis.tick_right()

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
        