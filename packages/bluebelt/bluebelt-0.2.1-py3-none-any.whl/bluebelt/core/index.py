import warnings
import datetime
import pandas as pd
import numpy as np

import bluebelt.core.decorators

@bluebelt.core.decorators.class_methods
@pd.api.extensions.register_index_accessor('blue')
class IndexToolkit():
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def alt(self, **kwargs):
        if isinstance(self._obj, pd.MultiIndex):
                
            if 'week' in self._obj.names:
                index = self._complete(iso=True)
                _index = np.array([datetime.datetime.fromisocalendar(*row).replace(tzinfo=datetime.timezone.utc).timestamp() for row in index], dtype='int')
                
            elif 'month' in self._obj.names:
                index = self._complete(iso=False)
                _index = np.array([datetime.datetime(*row).replace(tzinfo=datetime.timezone.utc).timestamp() for row in index], dtype='int')
        
        elif isinstance(self._obj, pd.DatetimeIndex):
            #_index = np.array([row.timestamp() for row in self._obj], dtype='int')
            return self._obj

        else:
            _index = self._obj

        # clean _index
        _index = _index - _index.min()
        _index = _index / np.gcd.reduce(_index)
        
        return _index

    def clean(self, **kwargs):
        # return a clean index for numpy calculations
        if isinstance(self._obj, pd.MultiIndex):
                
            if 'week' in self._obj.names:
                if self._obj.names == ['year', 'week', 'day']:
                    index = self._complete(iso=True)
                    _index = np.array([datetime.datetime.fromisocalendar(*row).replace(tzinfo=datetime.timezone.utc).timestamp() for row in index], dtype='int')
                else:
                    _index = np.arange(0, self._obj.shape[0])
                
            elif 'month' in self._obj.names:
                index = self._complete(iso=False)
                _index = np.array([datetime.datetime(*row).replace(tzinfo=datetime.timezone.utc).timestamp() for row in index], dtype='int')
        
        elif isinstance(self._obj, pd.DatetimeIndex):
            _index = np.array([row.timestamp() for row in self._obj], dtype='int')
            
        else:
            _index = self._obj

        # clean _index
        _index = _index - _index.min()
        _index = _index / np.gcd.reduce(_index)
        
        return _index

    def _complete(self, iso=True, levels=None):
        '''
        add missing levels to the (iso)datetimemultiindex
        '''
        _dict = self._obj.to_frame(index=False).to_dict()
        
        # set default dict
        if iso:
            _default_dict ={
                'year': {key: datetime.datetime.now().year for key in range(self._obj.shape[0])},
                'week': {key: 1 for key in range(self._obj.shape[0])},
                'day': {key: 1 for key in range(self._obj.shape[0])},
            }
        else:
            _default_dict = {
                'year': {key: datetime.datetime.now().year for key in range(self._obj.shape[0])},
                'month': {key: 1 for key in range(self._obj.shape[0])},
                'day': {key: 1 for key in range(self._obj.shape[0])},
                'hour': {key: 0 for key in range(self._obj.shape[0])},
                'minute': {key: 0 for key in range(self._obj.shape[0])},
                'second': {key: 0 for key in range(self._obj.shape[0])},
            }

        # add levels
        _levels = levels or _default_dict.keys()
        for level, data in _default_dict.items():
            if level in _levels:
                _dict[level] = _dict.get(level, _default_dict[level])

        return pd.MultiIndex.from_frame(pd.DataFrame.from_dict(_dict)[_default_dict.keys()])

    def to_isodatetimemultiindex(self, **kwargs):
        '''
        change the pandas.DatetimeIndex to a IsoDatetimeMultiIndex
        '''

        if isinstance(self._obj, pd.MultiIndex):
            return self._obj

        elif isinstance(self._obj, pd.DatetimeIndex):
                
            levels = ['year','week','day']
            level = kwargs.get('level', levels[-1])

            # get the levels
            if isinstance(level, str) and level in levels:
                levels = levels[:levels.index(level)+1]
            elif isinstance(level, list):
                _levels = [l for l in level if l in levels]
                if len(_levels) > 0:
                    levels = _levels

            frame = self._obj.isocalendar()[levels]

            return pd.MultiIndex.from_frame(frame[levels])

    iso = to_isodatetimemultiindex

    def to_datetimemultiindex(self, **kwargs):
        '''
        change the pandas.DatetimeIndex to a DatetimeMultiIndex
        '''

        if isinstance(self._obj, pd.MultiIndex):
            return self._obj
            
        elif isinstance(self._obj, pd.DatetimeIndex):
                        
            _dict = {
                'year': self._obj.year, # year including the century
                'month': self._obj.month, # month (1 to 12)
                'day': self._obj.day, # day of the month (1 to 31)
                #'hour': self._obj.hour, # hour, using a 24-hour clock (0 to 23)
                #'minute': self._obj.minute,
                #'second': self._obj.second,
            }
            
            level = kwargs.get('level', list(_dict.keys())[-1])

            # filter _dict with the levels
            if isinstance(level, str) and level in _dict.keys():
                _dict = {key: _dict[key] for key in list(_dict.keys())[:list(_dict.keys()).index(level)+1]}
            elif isinstance(level, list):
                _t_dict = {k: v for k, v in _dict.items() if k in level}
                if len(_t_dict) > 0:
                    _dict = _t_dict

            return pd.MultiIndex.from_frame(pd.DataFrame(_dict))
    
    dt = to_datetimemultiindex