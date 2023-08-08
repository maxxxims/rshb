import requests as r
import pandas as pd
from datetime import datetime
import utils
import numpy as np
from collections import Counter


token = ''
groups = {'svoe_rodnoe': 'svoerodnoe.rshb', 'esh_derevenskoe': 'eshderevenskoe', 'agromp': 'agromp'}


def get_users(token, groups):
    url = 'https://api.vk.com/method/groups.getMembers'
    data = r.get(url, params={'access_token': token, 'v': '5.131',
                                 'group_id': groups['esh_derevenskoe'],
                                 'offset': '0'}).json()['response']
    
    print(len(data['items']))
    print(data['items'][0], data['items'][1])


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
        print(self.counter)


    def parse_users_from_group(self, test=True):
        if test:
            i = 5000
        else:
            i = 0
        url = 'https://api.vk.com/method/groups.getMembers'
        data = r.get(url, params={'access_token': token, 'v': '5.131',
                                 'group_id': self.group,
                                 'offset': '0'}).json()['response']
        self.members = data['count']
        self.users += data['items']
        self.users_groups += [self.group] * self.members

        while  i * 1000 <= self.members:
            print(f'one request {i * 1000}, all = {self.members}')
            i += 1
            data = r.get(url, params={'access_token': token, 'v': '5.131',
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
            data_1000 = r.get(url, params={'access_token': token, 'v': '5.131',
                                    'user_ids': user_ids,
                                    'fields': utils.FIELDS}).json()['response']
            # print(len(data))
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
        for i in range(6722, len(self.users)):
            print(f'{i} / {len(self.users)}')
            try:
                url = 'https://api.vk.com/method/users.getSubscriptions'
                data = r.get(url, params={'access_token': token, 'v': '5.131',
                                        'user_id': self.users[i],
                                        'extended': 0}).json()
                if data.get('response', False):
                    common_groups += data['response']['groups']['items']
            
            except:
                print(f'error on step = {i}')
                #self.counter = Counter(common_groups)
                #self.save_counter(path_to_file='output_data/counter_save.csv')
                break

        self.counter = Counter(common_groups)


    def parse_all_groups(self, groups: dict):
        for key in groups.keys():
            self.set_group(groups[key])
            self.parse_users_from_group(test=False)
            self.parse_user_info(n_users='all')



    def save_df(self, path: str = 'users.csv'):
        self.df.to_csv(path, index=False)


    def save_counter(self, path_to_file: str = 'counter.csv'):
        with open(path_to_file, 'w') as f:
            for key in self.counter.keys():
                f.write(f'{key} {self.counter[key]}\n')

    
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


def parse_one_group(parser: Parser, group_name: str):
    parser.set_group(groups[group_name])
    parser.parse_users_from_group(test=False)
    print(len(parser.get_users()))
    print(len(parser.get_users_groups()))
    parser.parse_user_info(n_users=1)


def parse_list_of_groups(parser: Parser, group_list: list):
    for group in group_list:
        parser.set_group(group)
        parser.parse_users_from_group(test=False)
        # print(len(parser.get_users()))
        # print(len(parser.get_users_groups()))
    parser.parse_user_info(n_users='all')

        
def parse_all(parser: Parser):
    parser.parse_all_groups(groups)


def find_common_groups(parser: Parser, path_to_file: str):
    parser.load_users(path_to_file)
    parser.parse_common_groups()
    parser.save_counter(path_to_file='output_data/counter_2.csv')



def load_counter(parser: Parser, path_to_file: str):
    parser.load_counter(path_to_file)
    cnt = parser.get_counter()


if __name__ == '__main__':
    parser = Parser(token)
    #parse_list_of_groups(parser, group_list=[groups['svoe_rodnoe'], groups['agromp'], groups['esh_derevenskoe']])

    find_common_groups(parser, path_to_file='data_analysis/users_all2.csv')
    #load_counter(parser, path_to_file='output_data/counter.csv')
    #parser.save_df(path='data_analysis/users_all2.csv')
