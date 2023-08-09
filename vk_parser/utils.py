from datetime import datetime
import pandas as pd
import os 


DEFAULT_VALUE = None
FIELDS = 'bdate, city, home_town, occupation, relatives, sex, relation'

relation = {0: 'не указано', 1: 'не женат/не замужем', 2: 'есть друг/есть подруга;', 3: 'помолвлен/помолвлена',
            4: 'женат/замужем', 5: 'всё сложно', 6: 'в активном поиске', 7: 'влюблён/влюблена', 8: 'в гражданском браке'}


def GET_TOKEN() -> str:
    token = os.getenv('VK_TOKEN')
    if not token:
        with open('.env', 'r') as file:
            return file.read().replace(' ', '').split('=')[-1]
    return token

def get_age(date):
    if not date:
        return DEFAULT_VALUE
    elif date.count('.') == 2:
        return datetime.now().year - datetime.strptime(date, '%d.%m.%Y').year
    else:
        return DEFAULT_VALUE


def get_city(data):
    if not data:
        return DEFAULT_VALUE
    elif data.get('title', False):
        return data.get('title')
    else:
        return DEFAULT_VALUE
    

def get_home_town(data):
    if not data:
        return DEFAULT_VALUE
    elif data:
        return data
    else:
        return DEFAULT_VALUE
    

def get_occupation_type(data):
    if not data:
        return DEFAULT_VALUE
    elif data.get('type', False):
        if data.get('type') == 'university' and data.get('graduate_year', False):
            if data.get('graduate_year') < datetime.now().year:
                return 'end university'
            else:
                return 'university' 
        return data.get('type')
    else:
        return DEFAULT_VALUE
    

def get_relatives_number(data):
    if not data:
        return DEFAULT_VALUE
    elif data:
        return len(data)
    else:
        return DEFAULT_VALUE
    

def get_sex(data):
    if not data:
        return DEFAULT_VALUE
    elif data == 1:
        return 'w'
    elif data == 2:
        return 'm'
    else:
        return DEFAULT_VALUE
    
def get_relation(data):
    if not data:
        return 0, relation.get(0)
    elif data:
        return data, relation.get(data)
    else:
        return DEFAULT_VALUE