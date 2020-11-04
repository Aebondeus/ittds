"""
This is the part of app that serialize all data
from main app in json-format
"""



import json
import datetime
import os.path

days_of_the_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
monthnames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
daynames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" ]

def isleap(year:int):
    return year % 4 == 0 and (year % 100 != 0 and year % 400 == 0)

# original pattern for json-file
data = {
    'year_months':{k:0 for k in monthnames},
    'month_days':{k:0 for k in range(1, 32)},
    'week_days':{k:0 for k in daynames},
    'day_hours':{k:0 for k in range(24)},
    'buffer_zone':{
        'year':0, 'cur_month':(1, 'Jan'), 'cur_day':'',
        'cur_week':0, 'week_day':0,'day_hours':{}
    }
}

def update_data(year=0, month=(), day='', week_num=0, week_day=0, day_hours={}):
    '''
    Main update of data in json-file. Function fill json-file with data, that will be used for graphs.
    If data already in the json-file, this function check all values of current day, week, month,
    year and update data if it is need to.

    Soon i will change all arguments of this function in *args or **kwargs.

    For example, year=22, month=(3, 'Mar'), day='3', week_num=11, 
    day_hours={13:0, 14:50, 16:23, 17:11}. Months - 1-12. In this example
    the keys of the day_hours dict started from 13. It is because
    i want to give only the part of hours, from the moment when the timer is start
    '''
    kwargs = [year, month, day, week_num, week_day, day_hours]
    with open(os.path.dirname(os.path.abspath(__file__))+'\\test.json', 'r') as test: # path of the json-file will be changed
        f = json.load(test)

    # now we checking if our data is equal to data in buffer_zone
    # if it isn't - we must change some values
    if year != f['buffer_zone']['year']: # if curent year != year in buffer
        f['year_months']={k:0 for k in monthnames}

    if month[1] != f['buffer_zone']['cur_month'][1]: # month = (1, 'Jan')
        if month[0] == 2 and isleap(year): # if month is Feb and year is leap
            f['month_days'] ={str(k):0 for k in range(1, 30)}
        else:
            f['month_days'] = {str(k):0 for k in range(1, days_of_the_month[month[0]-1]+1)}

    # we will use date.isocalendar for this, but i don't like this flow
    if f['buffer_zone']['cur_week'] != week_num: 
        f['week_days'] = {k:0 for k in daynames}
    elif  year!=f['buffer_zone']['year']:
        f['week_days'] = {k:0 for k in daynames}

    # we also change day_hours data if we need it
    if f['buffer_zone']['cur_day'] != day:
        f['day_hours'] = {str(k):0 for k in range(24)}

    # finally we change all data in buffer_zone
    for k, v in zip(f['buffer_zone'], kwargs):
        f['buffer_zone'][k] = v
        print(f['buffer_zone'])

    update_graph_data(f, kwargs)

    with open(os.path.dirname(os.path.abspath(__file__))+'\\test.json', 'w') as test:
        json.dump(f, test, indent=2)

def update_graph_data(data:dict, data_list:list):
    """
    Update data for graphs and statistics. It worked when 
    timer stoped or when next hour is comming and we need 
    to fix previous value of minutes"""
    week_day = daynames[data_list[4]-1]
    month_day = data_list[2]
    month = data_list[1][1]

    for b_day in (data['buffer_zone']['day_hours']):
        data['day_hours'][b_day] += data['buffer_zone']['day_hours'][b_day]
    data['week_days'][week_day] = sum(list(data['day_hours'].values()))
    data['month_days'][month_day] = sum(list(data['day_hours'].values()))
    data['year_months'][month] = sum(list(data['month_days'].values()))

def get_data(key_to: str) -> dict:
    with open(os.path.dirname(os.path.abspath(__file__))+'\\test.json', 'r') as test:
        f = json.load(test)
    data = f[key_to]
    return data

try:
    with open(os.path.dirname(os.path.abspath(__file__))+'\\test.json', 'r') as test:
        pass
except OSError:
    with open(os.path.dirname(os.path.abspath(__file__))+'\\test.json', 'w') as test:
        json.dump(data, test, indent=2)



if __name__ == "__main__":
    print(os.path.dirname(os.path.abspath((__file__))))
