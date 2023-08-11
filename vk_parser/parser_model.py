import requests as r
import pandas as pd
from datetime import datetime
import utils
import numpy as np
from collections import Counter, defaultdict


class Parser:
    def __init__(self, token):
        self.token = token
        self.members = 0
        self.users = []
        self.users_groups = []
        self.group = None
        self.df = pd.DataFrame(columns=['id', 'age', 'city', 'occupation', 'sex', 'n_relatives', 'group', 'relation', 'relation_type'])
        self.counter = None


    def set_group(self, group):
        self.group = group
    

    def set_users(self, users: list):
        self.users = users


    def load_users(self, path_to_file: str):
        df = pd.read_csv(path_to_file)
        self.users = df['id'].to_numpy()
        self.users_groups = df['group'].to_numpy()


    def load_counter(self, path_to_file: str):
        with open(path_to_file, 'r') as f:
            self.counter = {}
            for el in f.read().split('\n'):
                s = el.split(' ')
                if len(s) == 2:
                    self.counter[s[0]] = s[1]
        #print(self.counter)


    def parse_users_from_group(self, test=True):
        if test:
            i = 5000
        else:
            i = 0
        url = 'https://api.vk.com/method/groups.getMembers'
        data = r.get(url, params={'access_token': self.token, 'v': '5.131',
                                 'group_id': self.group,
                                 'offset': '0'}).json()['response']
        self.members = data['count']
        self.users += data['items']
        self.users_groups += [self.group] * self.members

        while  i * 1000 <= self.members:
            print(f'one request {i * 1000}, all = {self.members}')
            i += 1
            data = r.get(url, params={'access_token': self.token, 'v': '5.131',
                                 'group_id': self.group,
                                 'offset': f'{i * 1000}'}).json()['response']
            self.users += data['items']


    def parse_user_info(self, n_users: int = 'all'):
        if n_users == 'all':
            n_users = len(self.users)

        url = 'https://api.vk.com/method/users.get'
        i = 0
        while i * 1000 <= n_users:
            user_ids = self.get_1000_users(i)
            data_1000 = r.get(url, params={'access_token': self.token, 'v': '5.131',
                                    'user_ids': user_ids,
                                    'fields': utils.FIELDS, 'lang': 'ru'}).json()['response']
            for data, u_index in zip(data_1000, [i * 1000 + j for j in range(len(data_1000))]):
                print(f'{u_index}/{n_users}')
                user = {
                    'id':            self.users[u_index],
                    'age':           utils.get_age(data.get('bdate', False)),
                    'occupation':    utils.get_occupation_type(data.get('occupation', False)),
                    'sex':           utils.get_sex(data.get('sex', False)),
                    'group':         self.users_groups[u_index],
                    'n_relatives':   utils.get_relatives_number(data.get('connections', False)),
                    'relation':      utils.get_relation(data.get('relation', False))[0],
                    'relation_type': utils.get_relation(data.get('relation', False))[1]
                }

                if not utils.get_city(data.get('city', False)):
                    user['city'] = utils.get_home_town(data.get('home_town', False))
                else:
                    user['city'] = utils.get_city(data.get('city', False))
                
                self.df = self.df.append(user, ignore_index=True)
            i += 1
        #print(self.df.head())


    def parse_common_groups(self):
        common_groups = []
        #for i in range(len(self.users)):
        for i in range(0, len(self.users)):
            print(f'{i} / {len(self.users)}')
            try:
                url = 'https://api.vk.com/method/users.getSubscriptions'
                data = r.get(url, params={'access_token': self.token, 'v': '5.131',
                                        'user_id': self.users[i],
                                        'extended': 0}).json()
                if data.get('response', False):
                    common_groups += data['response']['groups']['items']
            
            except:
                print(f'error on step = {i}')
                break

        self.counter = Counter(common_groups)


    def parse_all_groups(self, groups: dict):
        for key in groups.keys():
            self.set_group(groups[key])
            self.parse_users_from_group(test=False)
            self.parse_user_info(n_users='all')


    def merge_common_groups(self, groups: list):
        self.counter = {}
        for group in groups:
            with open(group, 'r') as f:
                for el in f.read().split('\n'):
                    s = el.split(' ')
                    if len(s) == 2:
                        self.counter[s[0]] = s[1]

        self.save_counter('output_data/counter_all.csv')

    def get_most_common_groups(self, limit: int = 10, save_file: bool = False):
        if type(self.counter) == dict:
            most_common = sorted(self.counter.items(), key=lambda x:  -int(x[1]))
            for i in range(limit):
                print(f'https://vk.com/public{most_common[i][0]}  common users = {most_common[i][1]}')

            if save_file:
                self.save_data(most_common, 'most_common_groups')

        else:
            print(Counter(self.counter).most_common(limit))
    

    def get_groups_types(self):
        url = 'https://api.vk.com/method/groups.getById'
        most_common_groups = sorted(self.counter.items(), key=lambda x:  -int(x[1]))
        activities = defaultdict(int)

        def _get_1000_groups_types(offset: int):
            group_ids = ''
            for i in range(offset * 1000, (offset + 1) * 1000):
                group_ids += f'{most_common_groups[i][0]}, '
            group_ids = group_ids[:-2]
            data = r.get(url, params={'access_token': self.token, 'v': '5.131',
                                    'group_ids': group_ids, 'fields': 'activity'
                                    }).json()['response']
            for el in data:
                if el.get('activity', False):
                    activities[el['activity']] += 1
        j = 0
        #while j * 1000 <= len(self.counter.items()):
        while j < 100: 
            print(f'{j} / 100')
            _get_1000_groups_types(j)
            j += 1

        most_common_types = sorted(activities.items(), key=lambda x:  -int(x[1]))

        for i in range(50):
            print(f'{most_common_types[i][0]}: {most_common_types[i][1]}')



    def save_df(self, path: str = 'users.csv'):
        self.df.to_csv(path, index=False)


    def save_counter(self, path_to_file: str = 'counter.csv'):
        with open(path_to_file, 'w') as f:
            for key in self.counter.keys():
                f.write(f'{key} {self.counter[key]}\n')


    def save_data(self, data: list, file_name: str):
        with open(f'output_data/{file_name}.txt', 'w') as f:
            for el in data:
                f.write(f'{el[0]}: {el[1]}\n')
    

    def get_1000_users(self, offset: int = 0):
        u = ''
        for user in range(offset * 1000, min(len(self.users), (offset + 1) * 1000)):
            u += f'{self.users[user]}, '
        return u[:-2]

    def get_users(self):
        return self.users
    
    def get_users_groups(self):
        return self.users_groups
    

    def get_counter(self):
        return self.counter



