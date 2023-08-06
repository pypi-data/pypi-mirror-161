#tdautils
current version: 1.1.9
installation:
pip install utautils (or pip install utautils --upgrade)
required package: pandas, os,datetime,pytz

tradedate_A
==============================================================================================
#initilize a tradedate_A obj with default start_date('2000-01-01'):
from tdautils import tda

#generate a datetime index of trading dates in Chinese stock market between '2010-01-01' and '2020-01-01', 
#non-trading start and end dates are offset
tda.gen_dtindex(start_date='2000-01-01',end_date='2020-01-01')
output:
DatetimeIndex(['2000-01-04', '2000-01-05', '2000-01-06', '2000-01-07',
               '2000-01-10', '2000-01-11', '2000-01-12', '2000-01-13',
               '2000-01-14', '2000-01-17',
               ...
               '2019-12-18', '2019-12-19', '2019-12-20', '2019-12-23',
               '2019-12-24', '2019-12-25', '2019-12-26', '2019-12-27',
               '2019-12-30', '2019-12-31'],
              dtype='datetime64[ns]', length=4846, freq=None)

#another way to generate datetime index using sample_size:
tda.gen_dtindex(start_date='2000-01-01',sample_size=10)
output:
DatetimeIndex(['2000-01-04', '2000-01-05', '2000-01-06', '2000-01-07',
               '2000-01-10', '2000-01-11', '2000-01-12', '2000-01-13',
               '2000-01-14', '2000-01-17'],
              dtype='datetime64[ns]', freq=None)

tda.gen_dtindex(end_date='2020-01-01',sample_size=10)
output:
DatetimeIndex(['2019-12-18', '2019-12-19', '2019-12-20', '2019-12-23',
               '2019-12-24', '2019-12-25', '2019-12-26', '2019-12-27',
               '2019-12-30', '2019-12-31'],
              dtype='datetime64[ns]', freq=None)

#tda.recent_td() return the most recent trade date in Chinese stock market calendar based on user's current time
tda.recent_td()
output:
'2021-08-20'

tool box
==============================================================================================
dateoffset(date,dtindex=None,offset=0,offset_method='ffill',boundin=False)
----------------------------
    Return the offset date from anchor date based on a reference dtindex
    
    Parameters
    ----------
    date :str
        anchor date for offseting
    dtindex : pd.DatetimeIndex,optional,default is None
        reference time index for performing the offset,if None Chinese stock market trade calendar is used 
    offset : int, optional,default is 0
        Position to be offset
    offset_method : str, optional,default is ffill
        when anchor date is not in the reference index,
        anchor date is auto offset to be the last/next/closest adjacent trade date based on offset_method = ffill/bfill/nearest
    boundin : TYPE, optional,default is False
        When offset date is outside the range of the reference time index, 
        exception will raise if boundin=False else the closest boundary date of the reference index is returned.  

example:
import pandas as pd
from tdautils import dateoffset
dtindex = pd.date_range(start='2021-08-01',end='2021-09-01',freq='B') #a datetime index with all the business dates in range
dateoffset(date='2021-08-21',dtindex=pd.date_range(start='2021-08-01',end='2021-09-01',freq='B')) #2021-08-21 is a non-business date in China-time calendar
output: Timestamp('2021-08-20 00:00:00', freq='B')


timenow(CN_time=True):
----------------------------
    Return the current time in pd.Timestamp
    
    Parameters
    ----------
    CN_time : bool,optional, default is True
        When CN_time = True, the return time is enforced to be the current China time regardless user's system time-zone setting

pro_ts (ts,time_format="date",mini_digit=2)
----------------------------
    Return time str(or list of str when pd.DatetimeIndex is provide) in the selected format

    Parameters
    ----------
    ts : pd.Timestamp or pd.DatetimeIndex
    
    time_format : str, optional,The default is "date"
        supported time_format:
            date: %Y-%m-%d
            date2: %Y%m%d
            week_time: %A, %Y-%m-%d %H:%M:%S
            week_time_CN: same as week_time but in Chinese for weekday
            time: %Y-%m-%d %H:%M:%S
            minitime:%Y-%m-%d %H:%M:%S.%f
            minitime2:%Y%m%d %H%M%S.%f
            time-only:%H:%M:%S
            minitime-only:%H:%M:%S.%f
            nt:%Y%m%d%H%M%S%f

    mini_digit: int, optional,The default is 2
        the numner of digit included in the return str for minisecond 
