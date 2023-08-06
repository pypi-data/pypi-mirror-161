import pandas as pd

def is_series(_obj):
    if not isinstance(_obj, pd.Series):
        raise ValueError(f'The object is expected to be a pandas Series, not {type(_obj).__name__}')
    
def is_frame(_obj):
    if not isinstance(_obj, pd.DataFrame):
        raise ValueError(f'The object is expected to be a pandas DataFrame, not {type(_obj).__name__}')
    
def is_series_or_frame(_obj):
    if not isinstance(_obj, (pd.Series, pd.DataFrame)):
        raise ValueError(f'The object is expected to be a pandas Series or DataFrame, not {type(_obj).__name__}')
    
def is_index(_obj):
    if not isinstance(_obj, pd.Index):
        raise ValueError(f'The object is expected to be a pandas Index, not {type(_obj).__name__}')
    
def is_datetimeindex(_obj):
    if not isinstance(_obj, pd.DatetimeIndex):
        raise ValueError(f'The object is expected to be a pandas DatetimeIndex, not {type(_obj).__name__}')

def is_multiindex(_obj):
    if not isinstance(_obj, pd.DatetimeIndex):
        raise ValueError(f'The object is expected to be a pandas MultiIndex, not {type(_obj).__name__}')

def has_datetimeindex(_obj):
    if not isinstance(_obj.index, pd.DatetimeIndex):
        raise ValueError(f'{type(_obj).__name__} is expected to have a DateTimeIndex, not a {type(_obj.index).__name__}')

def has_multiindex(_obj):
    if not isinstance(_obj.index, pd.DatetimeIndex):
        raise ValueError(f'{type(_obj).__name__} is expected to have a MultiIndex, not a {type(_obj.index).__name__}')