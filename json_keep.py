"""
This is the part of app that serialize all data
from main app in json-format. 
"""
import json
import datetime
import os.path

days_of_the_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
monthnames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
daynames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" ]

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
activities = {
    'Work':0, 'Study':0, 'Chill':0, 'Sport':0,
    'Games':0, 'Read':0, 'Cooking':0, 'Nothing':0
}
launches = {}
main_data = {
    'minutes_data':data,
    'activities_data':activities,
    'launches':launches,
    'button_pic':f'{os.path.dirname(os.path.abspath(__file__))}\\pics\\tomato.png',
    'stop_sound':f'{os.path.dirname(os.path.abspath(__file__))}\\sounds\\timer_bell.wav'
}

def get_pic() -> str:
    """Return the link to the picture"""
    with open(os.path.dirname(os.path.abspath(__file__))+'\\data.json', 'r') as test:
        test = json.load(test)
    pic = test['button_pic']
    return pic

def change_pic(link_to:str):
    """Change the link to the button picture in json-file"""
    with open(os.path.dirname(os.path.abspath(__file__))+'\\data.json', 'r') as test:
        f = json.load(test)
    f['button_pic'] = link_to
    with open(os.path.dirname(os.path.abspath(__file__))+'\\data.json', 'w') as test:
        json.dump(f, test, indent=2)

def get_sound() -> str:
    """Return the link to the sound"""
    with open(os.path.dirname(os.path.abspath(__file__))+'\\data.json', 'r') as test:
        test = json.load(test)
    sound = test['stop_sound']
    return sound

def change_sound(link_to:str):
    """Change the link to the sound in json-file"""
    with open(os.path.dirname(os.path.abspath(__file__))+'\\data.json', 'r') as test:
        f = json.load(test)
    f['stop_sound'] = link_to
    with open(os.path.dirname(os.path.abspath(__file__))+'\\data.json', 'w') as test:
        json.dump(f, test, indent=2)

def isleap(year:int):
    return year % 4 == 0 and (year % 100 != 0 and year % 400 == 0)


def update_data(data_lst:list):
    '''
    Main update of data in json-file. Function fill json-file with data, that will be used for graphs and tables.
    If data already in the json-file, this function check all values of current day, week, month,
    year and update data if it is need to.

    data in data_list:
    year=0, month=(), day='', week_num=0, week_day=0, day_hours={}, act='', l_tuple=().
    For example, year=2020, month=(3, 'Mar'), day='3', week_num=11, 
    day_hours={13:20}. act='Study', l_tuple=('60', '13.00-13.20', 'Learning Math', 'Study')
    '''

    with open(os.path.dirname(os.path.abspath(__file__))+'\\data.json', 'r') as json_data:
        modify_data = json.load(json_data)
        md = modify_data['minutes_data']
        ad = modify_data['activities_data']
        ld = modify_data['launches']

    launch = data_lst.pop(-1) 
    date = datetime.date.today().strftime('%d-%b-%Y')
    if not ld.get(date, None):
        ld[date] = []
    ld[date].insert(0, launch)

    act = data_lst.pop(-1)
    ad[act] += 1

    year, month, day, week_num, week_day, day_hours = data_lst

    # now we checking if our data is equal to data in buffer_zone
    # if it isn't - we must change some values
    if year != md['buffer_zone']['year']: # if curent year != year in buffer
        md['year_months']={k:0 for k in monthnames}

    if month[1] != md['buffer_zone']['cur_month'][1]: # month = (1, 'Jan')
        if month[0] == 2 and isleap(year): # if month is Feb and year is leap
            md['month_days'] ={str(k):0 for k in range(1, 30)}
        else:
            md['month_days'] = {str(k):0 for k in range(1, days_of_the_month[month[0]-1]+1)}

    if md['buffer_zone']['cur_week'] != week_num: 
        md['week_days'] = {k:0 for k in daynames}
    elif  year!=md['buffer_zone']['year']:
        md['week_days'] = {k:0 for k in daynames}

    # we also change day_hours data if we need it
    if md['buffer_zone']['cur_day'] != day:
        md['day_hours'] = {str(k):0 for k in range(24)}

    # finally we change all data in buffer_zone
    for k, v in zip(md['buffer_zone'], data_lst):
        md['buffer_zone'][k] = v

    update_graph_data(md, data_lst)

    with open(os.path.dirname(os.path.abspath(__file__))+'\\data.json', 'w') as json_data:
        json.dump(modify_data, json_data, indent=2)

def update_graph_data(data:dict, data_list:tuple):
    """
    Actually this function updates data for graphs and launches table
    """
    week_day = daynames[data_list[4]-1]
    month_day = data_list[2]
    month = data_list[1][1]

    for b_day in (data['buffer_zone']['day_hours']):
        data['day_hours'][b_day] += data['buffer_zone']['day_hours'][b_day]
    data['week_days'][week_day] = sum(list(data['day_hours'].values()))
    data['month_days'][month_day] = sum(list(data['day_hours'].values()))
    data['year_months'][month] = sum(list(data['month_days'].values()))


def get_bar_data(key_to: str) -> dict:
    """Return the data for a bar plot"""
    with open(os.path.dirname(os.path.abspath(__file__)) + '\\data.json', 'r') as json_data:
        dct = json.load(json_data)
        scope = dct['minutes_data']
    data = scope[key_to]
    return data

def get_pie_data() -> dict:
    """Return the data for a pie chart"""
    with open(os.path.dirname(os.path.abspath(__file__)) + '\\data.json', 'r') as json_data:
        dct = json.load(json_data)
        scope = dct['activities_data']
    return scope

def get_launch_data() -> dict:
    """Return the data for a table of launches"""
    with open(os.path.dirname(os.path.abspath(__file__)) + '\\data.json', 'r') as json_data:
        dct = json.load(json_data)
        scope = dct['launches']
    launch_dct = {}
    for str_date in scope:
        date = datetime.datetime.strptime(str_date, '%d-%b-%Y')
        launch_dct[date] = scope[str_date]
    return launch_dct

try:
    with open(os.path.dirname(os.path.abspath(__file__))+'\\data.json', 'r') as json_data:
        pass
except OSError:
    with open(os.path.dirname(os.path.abspath(__file__))+'\\data.json', 'w') as json_data:
        json.dump(main_data, json_data, indent=4)