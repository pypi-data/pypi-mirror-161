# -*- coding: utf-8 -*-
"""
Timeseries Utils

utils for process timeseries data

@author: YanJun
@date: 2022/02/24
"""


import pandas as pd
import numpy as np
import datetime

from constellations import GetConstellation
from Lunar import Lunar
from holiday import is_holiday




#%%

def df_dtype_convert(df:pd.DataFrame,
                     datetime_cols:list,
                     numeric_cols:list,
                     replaces:dict=dict()
                     )->pd.DataFrame:
    for col in datetime_cols:
        if col in df.columns:
            if col in replaces:
                for key in replaces[col]:
                    df[col].replace(key, replaces[col][key], inplace=True)
            df[col] = pd.to_datetime(df[col])
            
    for col in numeric_cols:
        if col in df.columns:
            if col in replaces:
                for key in replaces[col]:
                    df[col].replace(key, replaces[col][key], inplace=True)
            df[col] = pd.to_numeric(df[col])
            
    return df

#%%

def pd_freq2s(freq:str)->int:
    Number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    Unit = {
            'D':86400,
            'H':3600,
            'T':60,
            'MIN':60,
            'S':1,
            'L':1e-3,
            'MS':1e-3,
            'U':1e-6,
            'US':1e-6,
            'N':1e-9,
            'NS':1e-9,
            }
    if len(freq) < 2:
        return 0
    
    number = ''
    unit = ''
    for i,s in enumerate(freq):
        if s in Number:
            number += s
        else:
            unit = freq[i:].upper()
    number = float(number)
    if unit in Unit:
        return number * Unit[unit]
    else:
        return 0

#%%

TYPE_DATETIME = "Datetime"
TYPE_NUMBER = "Float"
TYPE_STR = "String"

def try_dtype(file:str)->dict:
    df = pd.read_csv(file)
    
    pass

#%%

COL_YEAR = "year"
COL_MONTH = "month"
COL_DAY = "day"
COL_DAYOFWEEK = "dayofweek" #星期几
COL_CONSTELLATION = "constellation" #星座
COL_LUNAR_MONTH = "lunarmonth"
COL_LUNAR_DAY = "lunarday"
COL_SOLAR_TERM = "solarterm" #节气
COL_SOLAR_TERM_NUMBER = "solarterm_number" #节气编号
COL_HOMEDAY = "homeday" #节假日
COL_HOLIDAY = "holiday" #节日
COL_HOLIDAY_NAME = "holidayname" #节日名

def export_info_datetime(df:pd.DataFrame,
                         index_is_datetime:bool,
                         datetime_col:str)->(pd.DataFrame,list):
    if index_is_datetime:
        if type(df.index) != pd.core.indexes.datetimes.DatetimeIndex:
            raise Exception('The dataframe index is not datetime')
            
        datetimes = np.array([pd.Timestamp(x).to_pydatetime() for x in df.index.values])
        datetime_col = "DateTime"
        df[datetime_col] = datetimes
        
    else:
        if not datetime_col in df.columns:
            raise Exception('Not datetime column in dataframe')
        df[datetime_col] = pd.to_datetime(df[datetime_col])
        
    df[COL_YEAR] = df[datetime_col].apply(lambda x: x.year)
    df[COL_MONTH] = df[datetime_col].apply(lambda x: x.month)
    df[COL_DAY] = df[datetime_col].apply(lambda x: x.day)
    df[COL_DAYOFWEEK] = df[datetime_col].apply(lambda x: x.weekday() + 1)
    df[COL_CONSTELLATION] = df[datetime_col].apply(lambda x: GetConstellation(x.month, x.day))
    df[COL_LUNAR_MONTH] = df[datetime_col].apply(lambda x: Lunar(x).ln_month())
    df[COL_LUNAR_DAY] = df[datetime_col].apply(lambda x: Lunar(x).ln_day())
    df[COL_SOLAR_TERM] = df[datetime_col].apply(lambda x: Lunar(x).ln_jie())
    df[COL_HOMEDAY] = df[datetime_col].apply(lambda x: is_holiday(x)[0])
    df[COL_HOLIDAY_NAME] = df[datetime_col].apply(lambda x: is_holiday(x)[1])
    df[COL_HOLIDAY] = df[datetime_col].apply(lambda x: is_holiday(x)[2])
    df[COL_SOLAR_TERM_NUMBER] = df[datetime_col].apply(lambda x: Lunar(x).ln_jieqi_number())
    df[COL_SOLAR_TERM_NUMBER].interpolate(inplace=True)
    df[COL_SOLAR_TERM_NUMBER].fillna(method='bfill', inplace=True)
    
    df.drop([COL_CONSTELLATION, COL_SOLAR_TERM, COL_HOLIDAY_NAME], axis=1, inplace=True)
    
    return df, [COL_YEAR, COL_MONTH, COL_DAY, COL_DAYOFWEEK, COL_LUNAR_MONTH, COL_LUNAR_DAY, COL_SOLAR_TERM_NUMBER, COL_HOMEDAY, COL_HOLIDAY]


#%%
    
def merge_ts_dataframe(df_main:pd.DataFrame,
                       df_other:list,
                       same_to_main:bool=False,
                       time_span:str='1H',
                       main_datetime_key:str="DateTime",
                       other_datetime_key:str="DateTime",
                       quantile:float=0.25,
                       agg_functions_main:dict=None,
                       agg_functions_other:list=None)->pd.DataFrame:
    if len(df_other) == 0:
        return df_main
    
    if type(df_main.index) != pd.core.indexes.datetimes.DatetimeIndex and not main_datetime_key in df_main.columns:
        raise Exception('Not datetime column in main dataframe')
        
    if same_to_main:
        new_df, time_span = equal_interval_ts(df_main, main_datetime_key, quantile, agg_functions_main)
    else:
        new_df = ts_resample(df_main, main_datetime_key, time_span, agg_functions_main)
        
    time_span_seconds = pd_freq2s(time_span)
    if time_span_seconds == 0:
        raise Exception('Time span freq error.')
        
    main_start_time = new_df.index[0]
        
    for i,df in enumerate(df_other):        
        if type(df.index) != pd.core.indexes.datetimes.DatetimeIndex and not other_datetime_key in df.columns:
            raise Exception('Not datetime column in other dataframe')
            
        if len(df) < 1:
            continue
        
        new_other_df = ts_resample(df, other_datetime_key, time_span, agg_functions_other[i])
        
        for i in range(len(new_other_df)):
            diff = new_other_df.index[0] - main_start_time
            diff = diff.value*1e-9
            if diff >=0 and diff <  time_span_seconds:
                if diff != 0:
                    offset = datetime.timedelta(seconds = diff)
                    new_other_df.index -= offset
                break      
        
        new_df = pd.concat([new_df, new_other_df], axis=1)
    
    return new_df

#%%

def guss_interval_ts(df:pd.DataFrame,
                     datetime_key:str,
                     quantile:float=0.25)->(str, str):
    '''
    找到最合适的时间序列数据步长
    
    Parameters
    ----------
    df : pd.DataFrame
        data.
    datetime_key : str
        datetime column name.
    quantile : float, optional
        percent used as time span. The default is 0.25.
        
    Raises
    ------
    Exception
        data has no datetime column.

    Returns
    -------
    timespan : int
        unit: nano second
    '''
    df_new = df.copy()
    df_new.dropna(inplace=True)
    if type(df_new.index) != pd.core.indexes.datetimes.DatetimeIndex:
        if not datetime_key in df.columns:
            raise Exception('Not datetime column in dataframe')
        df_new = df_dtype_convert(df_new, [datetime_key], [])
        df_new.index = df_new[datetime_key]        
    if type(df_new.index) != pd.core.indexes.datetimes.DatetimeIndex:
        raise Exception('Not a time series dataframe')
    df_diff = df_new.diff()
    df_diff.dropna(inplace=True)
    df_new.drop(datetime_key, axis=1, inplace=True)
    if df_diff[datetime_key].min() != df_diff[datetime_key].max():
        timespan = df_diff[datetime_key].quantile(quantile).value # unit: nano second
    else:
        timespan = df_diff[datetime_key].min().value
    return timespan

#%%

def equal_interval_ts(df:pd.DataFrame, 
                      datetime_key:str,
                      quantile:float=0.25,
                      agg_functions:dict=None)->(pd.DataFrame, str):
    '''
    将时间序列数据的步长变成一致的

    Parameters
    ----------
    df : pd.DataFrame
        data.
    datetime_key : str
        datetime column name.
    quantile : float, optional
        percent used as time span. The default is 0.25.
    agg_functions : dict, optional
        agg functions. The default is None.

    Raises
    ------
    Exception
        data has no datetime column.

    Returns
    -------
    df_new : pd.DataFrame
        new data frame.
    rule : str
        resample rule
    '''    
    df_new = df.copy()
    df_new.dropna(inplace=True)
    if type(df_new.index) != pd.core.indexes.datetimes.DatetimeIndex:
        if not datetime_key in df.columns:
            raise Exception('Not datetime column in dataframe')
        df_new.index = df_new[datetime_key]        
    if type(df_new.index) != pd.core.indexes.datetimes.DatetimeIndex:
        raise Exception('Not a time series dataframe')
    df_diff = df_new.diff()
    df_diff.dropna(inplace=True)
    df_new.drop(datetime_key, axis=1, inplace=True)
    if df_diff[datetime_key].min() != df_diff[datetime_key].max():
        timespan = df_diff[datetime_key].quantile(quantile).value # unit: nano second
        offset = datetime.timedelta(seconds = df_new.index[0].timestamp()%86400)
        df_new.index -= offset
        if agg_functions is not None:
            dfs = []
            for col in agg_functions.keys():
                df_tmp = df_new[col]
                if type(agg_functions[col]) is str:
                    if agg_functions[col] == 'interpolate':
                        df_tmp = df_tmp.resample(f'{timespan}ns').interpolate()
                    else:
                        df_tmp = df_tmp.resample(f'{timespan}ns').agg(agg_functions[col])
                else:
                    df_tmp = df_tmp.resample(f'{timespan}ns').apply(agg_functions[col])
                dfs.append(df_tmp)
            df_new = pd.concat(dfs, axis=1)
        else:
            df_new = df_new.resample(f'{timespan}ns').interpolate()
        df_new.index += offset
    else:
        timespan = df_diff[datetime_key].min().value
    return df_new, f'{timespan}ns'

def ts_resample(df:pd.DataFrame, 
                datetime_key:str,
                resample_rule:str,
                agg_functions:dict=None)->pd.DataFrame:
    
    df_new = df.copy()
    df_new.dropna(inplace=True)
    if type(df_new.index) != pd.core.indexes.datetimes.DatetimeIndex:
        if not datetime_key in df.columns:
            raise Exception('Not datetime column in dataframe')
        df_new.index = df_new[datetime_key]        
        if type(df_new.index) != pd.core.indexes.datetimes.DatetimeIndex:
            raise Exception('Not a time series dataframe')
    offset = datetime.timedelta(seconds = df_new.index[0].timestamp()%86400)
    df_new.index -= offset
    if agg_functions is not None:
        dfs = []
        for col in agg_functions.keys():
            df_tmp = df_new[col]
            if type(agg_functions[col]) is str:
                if agg_functions[col] == 'interpolate':
                    df_tmp = df_tmp.resample(resample_rule).interpolate()
                else:
                    df_tmp = df_tmp.resample(resample_rule).agg(agg_functions[col])
            else:
                df_tmp = df_tmp.resample(resample_rule).apply(agg_functions[col])
            dfs.append(df_tmp)
        df_new = pd.concat(dfs, axis=1)
    else:
        df_new = df_new.resample(resample_rule).interpolate()
    df_new.index += offset
    return df_new



#%%
def ts_sample_rolling(df:pd.DataFrame, 
                   features:list,
                   targets:list,
                   past:int,  
                   future:int,
                   step:int,
                   start_index:int=None, 
                   end_index:int=None)->(np.array, np.array):
    '''
    Sample from timeseries data. rolling window.
    
    Parameters
    ----------
        df : DataFrame
            data to be sampled
        features : list
            column names for x data
        targets:list
            column names for y data
        past : int
            window length for x data
        future : int
            window length for y data
        step : int
            window step
        start_index : int
            start index. The default is None.
        end_index:int
            end index. The default is None.
            
    Raises
    ------
    Exception
        data has not enough column.

    Returns
    -------
        x : np.array
            x data
        y : np.array
            y data
    '''
    for col in features:
        if not col in df:
            raise Exception(f'df has no {col} column.')
    for col in targets:
        if not col in df:
            raise Exception(f'df has no {col} column.')
    if start_index is None:
        start_index = 0
    if end_index is None:
        end_index = len(df) - 1
    count_samples = (end_index - start_index + 1 - past - future)//step + 1
    x = []
    y = []
    for i in range(count_samples):
        one_x = df[features][start_index+i*step:start_index+i*step+past].values
        one_x = one_x.astype('float32')
        one_y = df[targets][start_index+i*step+past:start_index+i*step+past+future].values
        one_y = one_y.astype('float32')
        x.append(one_x)
        y.append(one_y)
        
    x = np.array(x)
    y = np.array(y)
    
    return x, y

def ts_sample_rolling_multX(df:pd.DataFrame, 
                   features:list,
                   targets:list,
                   past:int,  
                   future:int,
                   step:int,
                   start_index:int=None, 
                   end_index:int=None)->(np.array, np.array, np.array):
    '''
    Sample from timeseries data. rolling window.
    2-head x data.
    1). past x data: all features, length is past
    2). future x data: features that not in targets, length is future
    
    Parameters
    ----------
        df : DataFrame
            data to be sampled
        features : list
            column names for x data
        targets:list
            column names for y data
        past : int
            window length for x data
        future : int
            window length for y data
        step : int
            window step
        start_index : int
            start index. The default is None.
        end_index:int
            end index. The default is None.
            
    Raises
    ------
    Exception
        data has not enough column.

    Returns
    -------
        x1 : np.array
            past x data
        x2 : np.array
            future x data
        y : np.array
            y data
    '''
    future_features = []
    for col in features:
        if not col in df:
            raise Exception(f'df has no {col} column.')
        if not col in targets:
            future_features.append(col)
    for col in targets:
        if not col in df:
            raise Exception(f'df has no {col} column.')
    if start_index is None:
        start_index = 0
    if end_index is None:
        end_index = len(df) - 1
    count_samples = (end_index - start_index + 1 - past - future)//step + 1
    x1 = []
    x2 = []
    y = []
    for i in range(count_samples):
        one_x1 = df[features][start_index+i*step:start_index+i*step+past].values
        one_x1 = one_x1.astype('float32')
        one_x2 = df[future_features][start_index+i*step+past:start_index+i*step+past+future].values
        one_x2 = one_x2.astype('float32')
        one_y = df[targets][start_index+i*step+past:start_index+i*step+past+future].values
        one_y = one_y.astype('float32')
        x1.append(one_x1)
        x2.append(one_x2)
        y.append(one_y)
        
    x1 = np.array(x1)
    x2 = np.array(x2)
    y = np.array(y)
    
    return x1, x2, y

#%%
    
def ts_sample_synchro_rolling(df:pd.DataFrame, 
                              features:list,
                              targets:list,
                              sequence_length:int,  
                              step:int,
                              start_index:int=None, 
                              end_index:int=None)->(np.array, np.array):
    '''
    Sample from timeseries data. rolling window.
    
    Parameters
    ----------
        df : DataFrame
            data to be sampled
        features : list
            column names for x data
        targets:list
            column names for y data
        sequence_length : int
            window length for x/y data
        step : int
            window step
        start_index : int
            start index. The default is None.
        end_index:int
            end index. The default is None.
            
    Raises
    ------
    Exception
        data has not enough column.

    Returns
    -------
        x : np.array
            x data
        y : np.array
            y data
    '''
    for col in features:
        if not col in df:
            raise Exception(f'df has no {col} column.')
    for col in targets:
        if not col in df:
            raise Exception(f'df has no {col} column.')
    if start_index is None:
        start_index = 0
    if end_index is None:
        end_index = len(df) - 1
    count_samples = (end_index - start_index + 1 - sequence_length)//step + 1
    x = []
    y = []
    for i in range(count_samples):
        one_x = df[features][start_index+i*step:start_index+i*step+sequence_length].values
        one_x = one_x.astype('float32')
        one_y = df[targets][start_index+i*step:start_index+i*step+sequence_length].values
        one_y = one_y.astype('float32')
        x.append(one_x)
        y.append(one_y)
        
    x = np.array(x)
    y = np.array(y)
    
    return x, y

#%%

def rebuild_from_rolling_sample(data:np.array, 
                                cols:list,
                                step:int,
                                start_index:int=None, 
                                end_index:int=None,
                                keep_tail=True,
                                **args)->pd.DataFrame:
    if len(data.shape) != 3:
        raise Exception('The data must be a 3-dimension array')
        
    if data.shape[2] != len(cols):
        raise Exception(f'Get {len(cols)} cols, but the last dimension of data is {data.shape[2]}')
        
    if data.shape[1] < step:
        raise Exception(f'The 2nd dimension of data is f{data.shape[1]}, is less than the step')
        
    if start_index is None:
        start_index = 0
    if end_index is None:
        end_index = data.shape[0]
        
    x = []
    for i in range(start_index, end_index):
        for j in range(step):
            x.append(data[i][j])
    
    if keep_tail:
        for j in range(data.shape[1] - step):
            x.append(data[-1][step+j])
    
    x = np.array(x)
    
    df = pd.DataFrame(x, columns=cols)
    
    if 'datetime_index' in args and 'past_steps' in args:
        df.index = args['datetime_index'][args['past_steps']:args['past_steps']+len(df)]
    
    return df

#%%
    
def ts_split_rollingY(df:pd.DataFrame,
                      past:int,  
                      future:int,
                      step:int,
                      start_index:int=None, 
                      end_index:int=None,
                      usecols:list=None
                      )->pd.DataFrame:
    if start_index is None:
        start_index = 0
    if end_index is None:
        end_index = len(df) - 1
        
    count_samples = (end_index - start_index + 1 - past - future)//step + 1
    target_length = (count_samples - 1)*step + future
    if usecols is None:
        return df[start_index+past:start_index+past+target_length]
    else:
        return df[usecols].iloc[start_index+past:start_index+past+target_length]
    


