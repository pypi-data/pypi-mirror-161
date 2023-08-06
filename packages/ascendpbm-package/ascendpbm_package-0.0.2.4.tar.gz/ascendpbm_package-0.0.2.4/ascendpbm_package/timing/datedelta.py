import datetime as dt
from math import ceil

class Quarter():

    def __init__(self, og_date):
        self.og_date = self.convert_to_date_obj(og_date)
        self.quarter = self.get_quarter(self.og_date)
        self.quarter_start= self.get_first_day_of_the_quarter(self.og_date)
        self.quarter_end = self.get_last_day_of_the_quarter(self.og_date)
        self.prev_quarter_start, self.prev_quarter_end = self.get_start_end_dates_last_quarter(self.og_date)
        self.next_quarter_start, self.next_quarter_end = self.get_start_end_dates_next_quarter(self.og_date)
        self.year = self.quarter_end.year


    def convert_to_date_obj(self, p_date):
        if type(p_date) == (dt.date or dt.datetime):
            return p_date
        elif type(p_date) == str:
            p_len = len(p_date)
            # strips extra stuff from date string such as time stamp
            if p_len > 10:
                p_date = p_date[:10]
            if p_len >= 8:
                if p_date.find('/') > 0:
                    p_date_parts = p_date.split('/')
                    p_date = dt.datetime(int(p_date_parts[2]), int(p_date_parts[0]), int(p_date_parts[1]))
                    #p_date = dt.datetime.strptime(p_date, '%m/%d/%Y')
                elif p_date.find('-') > 0:
                    p_date_parts = p_date.split('-')
                    p_date = dt.datetime(int(p_date_parts[2]), int(p_date_parts[0]), int(p_date_parts[1]))
                else:
                    try:
                        print('Date format assumed as "yyyymmdd". Please check og_date looks correct')
                        p_date = dt.datetime.strptime(p_date, '%Y%m%d')
                    except:
                        print('Date format assumed as "mmddyyyy". Please check og_date looks correct')
                        p_date = dt.datetime.strptime(p_date, '%m%d%Y')
            elif p_len == 6:
                try:
                    print('Date format assumed as "yymmdd". Please check og_date looks correct')
                    p_date = dt.datetime.strptime(p_date, '%y%m%d')
                except:
                    print('Date format assumed as "mmddyy". Please check og_date looks correct')
                    p_date = dt.datetime.strptime(p_date, '%m%d%y')
        return p_date

    def __repr__(self):
        return f'{self.quarter}Q{self.year}'

    def __str__(self):
        return f'{self.quarter}Q{self.year}'

    def get_quarter(self, p_date) -> int:
        return (p_date.month - 1) // 3 + 1

    def get_first_day_of_the_quarter(self, p_date: dt.date) -> dt.datetime:
        return dt.datetime(p_date.year, 3 * ((p_date.month - 1) // 3) + 1, 1)

    def get_last_day_of_the_quarter(self, p_date: dt.date) -> dt.datetime:
        quarter = self.get_quarter(p_date)
        return dt.datetime(p_date.year + 3 * quarter // 12, 3 * quarter % 12 + 1, 1) + dt.timedelta(days=-1)

    def get_start_end_dates_last_quarter(self, p_date: dt.date) -> tuple:
        cur_startquarter_date = self.get_first_day_of_the_quarter(p_date)
        p_date = cur_startquarter_date - dt.timedelta(days=1)

        last_quarter_start_date = self.get_first_day_of_the_quarter(p_date)
        last_quarter_end_date = self.get_last_day_of_the_quarter(p_date)
        return (last_quarter_start_date, last_quarter_end_date)
    
    def get_start_end_dates_next_quarter(self, p_date: dt.date) -> tuple:
        cur_endquarter_date = self.get_last_day_of_the_quarter(p_date)
        p_date = cur_endquarter_date + dt.timedelta(days=1)

        next_quarter_start_date = self.get_first_day_of_the_quarter(p_date)
        next_quarter_end_date = self.get_last_day_of_the_quarter(p_date)
        return (next_quarter_start_date, next_quarter_end_date)

def monthdelta(months=0,operation='add',date=None):
    """Adds or removes the specified from number of months from a given date.
    It will leave the day of the month intact unless it is outside the end of the month (29,30,31)"""
    if date == None:
        date = dt.datetime.now()
    if operation == 'add':
        newmonth = date.month + months
        def correct_month_year_add(year, newmonth):
            newyear = year
            if newmonth > 12:
                newmonth = newmonth - 12
                newyear = newyear + 1
                newyear, newmonth = correct_month_year_add(newyear, newmonth)
            return (newyear, newmonth)
        newyear, newmonth = correct_month_year_add(date.year, newmonth)
    if operation == 'subtract':
        newmonth = date.month - months
        def correct_month_year_sub(year, newmonth):
            newyear = year
            if newmonth <= 0:
                newmonth = 12 + newmonth
                newyear = newyear - 1
                newyear, newmonth = correct_month_year_sub(newyear, newmonth)
            return (newyear, newmonth)
        newyear, newmonth = correct_month_year_sub(date.year, newmonth)
    try:
        newdate = dt.datetime(year=newyear, month=newmonth, day=date.day)
    except ValueError as e:
        end_of_months = [31,30,29,28]
        if str(e) == 'day is out of range for month':
            for day in end_of_months:
                try:
                    newdate = dt.datetime(year=newyear, month=newmonth, day=day)
                    break
                except:
                    continue
    return newdate


def get_all_rundates(start_date, end_date, period):
    '''A function to generate date objects for every historical run date
    given today's date.
    Takes two date objects for the start and end of a time interval,
    takes a period of days as int,
    returns generator of date objects.
    It should give back only full slices (e.g., dates of periodic weeks)
    without giving back the next scheduled run date if we're not there yet
    (unless you supply with a future date).'''
    top = int((end_date - start_date).days)+1
    for n in range(0, int(period*ceil(top/period)), period):
        yield start_date + dt.timedelta(n)
        
        