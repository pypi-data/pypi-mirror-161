# -*- coding: utf-8 -*-
"""
Chinese stock market tradedate utility
中国A股日历量化工具包 - 中文说明: www.topfintel.com/tdautils

"This package includes a collection of tools for  offseting, 
generating trade date series used in quant analysis. 
Based on a pre-saved Chinese stock market calendar (since year 1991), 
this package enables user to quickly find trade date(e,g the most recent trade date, 
a offset trade date from an anchor date) 
or generate a user-specified datetime index for back-testing or quant modeling"

"""

__author__ = "Dr.EdwC  (ed@topfintech.org)" 
__version__ = "1.1.7"
__copyright__ = "Copyright (c) 2020-2021 ed@topfintech.org by the MIT license"
__license__ = "MIT"
__yrange__ = [1991,2022]
__dependencies__ = ["pandas"]
missing_d = []

for d in __dependencies__:
    try:
        __import__(d)
    except ImportError as e:
        missing_d.append(f"{d}: {e}")

if missing_d:
    raise ImportError(
        "Unable to import required dependencies:\n" + "\n".join('missing_dependencies')
    )
del d, missing_d

import pandas as pd
import datetime
import pytz
from tdautils.data import non_tradedate_A
__ntb_list__ = non_tradedate_A.ntb_list

def dateoffset(date,dtindex=None,offset=0,offset_method='ffill',boundin=False):   
    """
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

    """
    
    
    if isinstance(date,str):
        try:
            pddate=pd.Timestamp(date)
        except:
            raise ValueError("dayoffset~cannot convert str to pd.Timestamp")
    elif not isinstance(date,(pd.Timestamp,datetime.datetime)):
        raise TypeError("dayoffset~only date str or timestamp objects are allowed,instead you provide %s" %(date))
    else:
        pddate=date
    if len(dtindex)==0:
        raise ValueError("dayoffset~input dtindex is empty")
    if not isinstance(dtindex,pd.DatetimeIndex):
        raise TypeError("dayoffset~dtindex input is not pd.DatetimeIndex")
    if pddate<dtindex[0] or pddate>dtindex[-1]:
        if boundin:
            if pddate<dtindex[0]:
                return dtindex[0]
            else:
                return dtindex[-1]
        else:
            raise RuntimeError(f"dayoffset~ date input {pddate} is out of range of the ref dtindex")
         
    pddate_loc = dtindex.get_indexer([pddate],method=offset_method)
    if pddate_loc+offset <0 or  pddate_loc+offset > len(dtindex)-1:
        if boundin:
            if pddate_loc+offset <0:
                return dtindex[0]
            if pddate_loc+offset > len(dtindex)-1:
                return dtindex[-1]
        else:
            raise RuntimeError("offset value out of bound")
    else:
        return dtindex[pddate_loc+offset]
    
def timenow(CN_time=True):
    """
    Return the current time in pd.Timestamp
    
    Parameters
    ----------
    CN_time : bool, optional, default is True
        When CN_time = True, the return time is enforced to be the current China time regardless user's system time-zone setting

    """
    if CN_time:
        return pd.Timestamp.today(tz=pytz.timezone('Asia/Shanghai')).replace(tzinfo=None)
    else:
        return pd.Timestamp.today()
    
def pro_ts(ts,time_format="date",mini_digit=2):
    """
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

    """
    if isinstance(ts,str):
        ts = pd.Timestamp(ts)
    if time_format=="date":
        return ts.strftime("%Y-%m-%d")
    elif time_format=="date2":
        return ts.strftime("%Y%m%d")
    elif time_format == "week_time":
        return ts.strftime("%A, %Y-%m-%d %H:%M:%S")
    elif time_format == "week_time_CN":
        rt = ts.strftime("%A, %Y-%m-%d %H:%M:%S").replace("Monday","星期一").replace("Tuesday","星期二").replace("Wednesday","星期三").replace(
                        "Thursday","星期四").replace("Friday","星期五").replace("Saturday","星期六").replace("Sunday","星期日")
        return rt
    elif time_format == "time":
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    elif time_format == "minitime":
        return ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-(6-mini_digit)]
    elif time_format == "minitime2": #for file name
        return ts.strftime("%Y%m%d %H%M%S.%f")
    elif time_format == "time-only":
        return ts.strftime("%H:%M:%S")
    elif time_format == "minitime-only":
        return ts.strftime("%H:%M:%S.%f")[:-(6-mini_digit)]
    elif time_format == "nt":
        return ts.strftime("%Y%m%d%H%M%S%f")
    else:
        raise ValueError ("unsupported time format")


class tradedate_A():
    """
    The text file including all non-trading business in Chinese calendar is loaded at initlization. 
    The file comes with the package. 
    """
    
    def __init__(self,auto_load=True,start_date='2000-01-01'):
        self.__calendar = None
        self.init_calendar() 
        self.__start_date=start_date #make the tradedate calendar smaller speeds up dateoffset
        self.update_dtindex(start_date=self.__start_date)
    
    @property
    def start_date(self):
        return self.__start_date
    
    @property
    def calendar(self):
        return self.__calendar

    @property
    def tradedate(self):
        return self.__tradedate
    
    def init_calendar(self,extra=None):
        """
        load the non-trading business dates and generate the calendar
        Parameters
        ----------
        extra : TYPE,list,default = None
            This is for generating case-specified calendar for particular market or stock
            extra non-trading business dates may be provided here

        Returns
        -------
        None.

        """
        if __yrange__[-1]<timenow().year:
            print ('warning! tdautils calendar is outdated, updated the package may resolve this issue!')
        ntdf = __ntb_list__
        self.__calendar = pd.Series(1,dtype=object,index=pd.date_range(start=f'{__yrange__[0]}-01-01',end=f'{__yrange__[1]}-12-31'))
        self.__calendar.loc[ntdf] = 0
        self.__calendar[(self.__calendar.index.weekday == 5) | (self.__calendar.index.weekday == 6)] = 0
        if extra is not None:
            self.__calendar.loc[extra] = 0
        
        
        
    def gen_dtindex(self,end_date=None,start_date=None,sample_size=None,include_ct=True,offset=0,cy=False):
        """
        generate a trade_date series of pd.DatetimeIndex type with date range controls.
        
        Parameters
        ----------
        end_date : str, optional,The default is None
            specify the end_date of the trade_date series,non-trading date will be auto offset by bfill
        start_date : str, optional,The default is None
            specify the start_date of the trade_date series,non-trading date will be auto offset by ffill
        sample_size : int, optional,The default is None
            if only one of the start_date and end_date is provided, sample_size is used to specify 
            how many trading days of the generated series,size may be truncated if boundaries of self.tradedate is reached  
        include_ct : bool, optional, default is True
            if end_date is used to specified the series, include ct specify whether the current day should
            be included. If include_ct=True, return series includes the current date when the method is called
        offset : int, optional default is 0
            offset the end_date and start_date by the input step
        cy : bool, optional,default is False
            A shortcut parameter which ignore other parameter to return current year's tradedate index

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        if self.__calendar is None:
            raise ValueError('calendar is not initilized')
        

        
        if start_date is None and sample_size is None and end_date is None:
            if cy:
                return self.__tradedate[self.__tradedate.year==timenow().year]
            else:
                return self.__tradedate
        else:
            dtindex =pd.DatetimeIndex(self.calendar[self.calendar==1].index)
            if start_date is not None and sample_size is not None and end_date is not None:
                sd = dateoffset(start_date,dtindex=dtindex,offset_method='bfill',offset=0,boundin=False)
                ed = dateoffset(end_date,dtindex=dtindex,offset_method='ffill',offset=0,boundin=False)
                rindex =self.__calendar.loc[dtindex].loc[sd:ed].index   
                if len(rindex)>sample_size:
                    return rindex[-sample_size:]
                else:
                    return rindex
            
            if sample_size == None or ((start_date is not None) and (end_date is not None)):
                if start_date is None:
                    sd = self.__tradedate[0]
                else:
                    sd = dateoffset(start_date,dtindex=dtindex,offset_method='bfill',offset=0,boundin=False)
                if end_date is None:
                    if include_ct:
                        ed = self.__tradedate[-1]
                    else:
                        if timenow().weekday()>4:
                            end_date = self.__tradedate[-1]
                        else:
                            end_date = self.__tradedate[-2]
                else:
                    ed = dateoffset(end_date,dtindex=dtindex,offset_method='ffill',offset=0,boundin=False)
                if sd>ed:
                    raise ValueError("sd>ed")
                if offset!=0:
                    sd = dateoffset(sd,dtindex=dtindex,offset=offset,boundin=True)
                    ed = dateoffset(ed,dtindex=dtindex,offset=offset,boundin=True)
                return self.__calendar.loc[dtindex].loc[sd:ed].index
            else:
                if start_date is None:
                    if end_date is None:
                        end_date = self.__tradedate[-1]
                    ed = dateoffset(end_date,dtindex=dtindex,offset_method='ffill',offset=0,boundin=False)
                    if offset!=0:
                        ed = dateoffset(ed,dtindex=dtindex,offset=offset,boundin=True)
                    return self.__calendar.loc[dtindex].loc[:ed].index[-sample_size:]
                else:
                    sd = dateoffset(start_date,dtindex=dtindex,offset_method='bfill',offset=0,boundin=False)
                    if end_date is None:
                        end_date = self.__tradedate[-1]
                    if offset!=0:
                        sd = dateoffset(sd,dtindex=dtindex,offset=offset,boundin=True)
                    return self.__calendar.loc[dtindex].loc[sd:end_date].index[:sample_size]                    
    
    def recent_td(self,return_str=True):   
        """
        return the most recent trade date: return the current date if today is a trading day 
        otherwise return the most recent trading date in the calendar  

        Parameters
        ----------
        return_str : bool
            return pd.Timestamp if False else data str
        """
        self.update_dtindex()
        if return_str:
            return pro_ts(self.__tradedate[-1])
        else:
            return self.__tradedate[-1]
    
    def ntd(self,end_date=None,start_date=None):
        """
        Return the non-trading dates within a calendar range specified by start_date,end_date parameters (inclusive)

        Parameters
        ----------
        end_date : str, optional,default is None.
            end_date in calendar 
        start_date : str, optional,default is None.
            start_date in calendar 

        """
        if end_date is None:
            end_date = pro_ts(timenow())
        if start_date is None:
            start_date = self.__tradedate[0]
        cal = self.__calendar.loc[start_date:end_date]
        return cal[cal==0].index
        
    def dateoffset(self,date=None,offset=0,offset_method='ffill',boundin=False):
        """
        same as dateoffset above with dtindex specified by self.__tradedate

        """
        if date is None:
            date = self.__tradedate[-1]
        dtindex = self.__calendar[self.__calendar==1].index
        return dateoffset(date,dtindex=dtindex,offset=offset,offset_method=offset_method,boundin=boundin) 
    
    def update_dtindex(self,start_date=None):
        """
        update self.__tradedate based on current time and calendar
        
        """
        if self.__calendar is not None:
            self.__tradedate = self.__calendar[self.__calendar==1].loc[start_date:pro_ts(timenow())].index
        self.__tradedate.name = "date"

tda = tradedate_A()

