import pandas as pd
import pdb,datetime
import dateutil.parser as dt_parser

def convert_date(date, format='%Y-%m-%d'):
    try:
        if isinstance(date, str):
            date = dt_parser.parse(date)
    except Exception as e:
        raise Exception('date:{}格式不能识别。'%date)

    return date#.strftime(format)


class Calendar(object):
    @classmethod 
    def get_alldates(cls, begin_date=None, end_date=None, trade_date=None, 
                 horizon=None, reverse=False):
        if trade_date is not None and horizon is not None:
            end_date = convert_date(trade_date) if isinstance(trade_date,str) else trade_date
            begin_date = end_date - datetime.timedelta(days=int(horizon[1:-1]))
        
        if begin_date is not None and end_date is not None:
            end_date = convert_date(end_date) if isinstance(end_date,str) else end_date
            begin_date = convert_date(begin_date) if isinstance(begin_date,str) else begin_date
            dates = [(end_date - datetime.timedelta(days= i)) for i in range(0, (end_date-begin_date).days + 1)]
        else:
            dates = []
        dates.sort(reverse=False)
        return dates
            
     
    @classmethod
    def get_dates(cls, holidayCenter=None, begin_date=None, end_date=None, trade_date=None, 
                 horizon=None):
        if holidayCenter is None:
            return cls.get_alldates(begin_date=begin_date, end_date=end_date, trade_date=trade_date, 
                 horizon=horizon)
     
    
    @classmethod
    def weekend_dates(cls, holidayCenter=None, begin_date=None, end_date=None, trade_date=None, 
                 horizon=None, is_all=False):
        dates = cls.get_dates(holidayCenter=holidayCenter, begin_date=begin_date, end_date=end_date, trade_date=trade_date, 
                 horizon=horizon)
        dates = pd.DataFrame(dates,columns=['dates'])
        dates['week'] = dates['dates'].apply(lambda x: x.year * 10000  + x.week)
        week_end = dates.groupby('week').apply(lambda x: x['dates'].values[0])
        return [d.date() for d in week_end if d.to_pydatetime().weekday() == 0]
    
    @classmethod
    def monthend_dates(cls, holidayCenter=None, begin_date=None, end_date=None, trade_date=None, 
                 horizon=None, is_all=False):
        def is_monthend(date):
            next_month = date.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
            monthend_date = next_month - datetime.timedelta(days=next_month.day)
            return (monthend_date - date).days
        
        dates = cls.get_dates(holidayCenter=holidayCenter, begin_date=begin_date, end_date=end_date, trade_date=trade_date, 
                 horizon=horizon)
        dates = pd.DataFrame(dates,columns=['dates'])
        dates['month'] = dates['dates'].apply(lambda x: x.year * 100  + x.month)
        month_end = dates.groupby('month').apply(lambda x: x['dates'].values[-1])
        return [d.date() for d in month_end.tolist() if is_monthend(d) == 0]
    
    @classmethod
    def quarterend_dates(cls, holidayCenter=None, begin_date=None, end_date=None, trade_date=None, 
                 horizon=None, is_all=False):
        def is_quarterend(date):
            quarter = int((date.month - 1) / 3 + 1)
            month = int(3 * quarter)
            remaining = int(month / 12)
            quarterend_date = datetime.datetime(date.year + remaining, month % 12 + 1, 1) + datetime.timedelta(days=-1)
            return (quarterend_date.date() - date).days
        
        dates = cls.get_dates(holidayCenter=holidayCenter, begin_date=begin_date, end_date=end_date, trade_date=trade_date, 
                 horizon=horizon)
        dates = pd.DataFrame(dates,columns=['dates'])
        dates['quarter'] = dates['dates'].apply(lambda x: x.year * 10000  + x.quarter)
        quarter_end = dates.groupby('quarter').apply(lambda x: x['dates'].values[-1])
        return [d.date() for d in quarter_end.tolist() if is_quarterend(d.date())==0]
    
    
    @classmethod
    def yearend_dates(cls, holidayCenter=None, begin_date=None, end_date=None, trade_date=None, 
                 horizon=None, is_all=False):
        def is_yearend(date):
            yearend_date = datetime.date(year=date.year, month=12, day=31)
            return (yearend_date - date).days
        
        dates = cls.get_dates(holidayCenter=holidayCenter, begin_date=begin_date, end_date=end_date, trade_date=trade_date, 
                 horizon=horizon)
        dates = pd.DataFrame(dates,columns=['dates'])
        dates['year'] = dates['dates'].apply(lambda x: x.year * 100)
        year_end = dates.groupby('year').apply(lambda x: x['dates'].values[-1])
        return [d.date() for d in year_end.tolist() if is_yearend(d.date())==0]
    
    
    
        
        

        