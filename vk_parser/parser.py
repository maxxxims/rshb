import requests as r
import pandas as pd
from datetime import datetime
import utils



groups = {'svoe_rodnoe': 'svoerodnoe.rshb', 'esh_derevenskoe': 'eshderevenskoe'}


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
        self.members = None
        self.users = []
        self.group = None
        self.df = pd.DataFrame(columns=['id', 'age', 'city', 'occupation', 'sex', 'n_relatives', 'group', 'relation', 'relation_type'])


    def set_group(self, group):
        self.group = group
    

    def set_users(self, users):
        self.users = users


    def parse_users_from_group(self):
        offset = 1000
        i = 5000
        url = 'https://api.vk.com/method/groups.getMembers'
        data = r.get(url, params={'access_token': token, 'v': '5.131',
                                 'group_id': self.group,
                                 'offset': '0'}).json()['response']
        self.members = data['count']
        self.users += data['items']

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
        for i in range(n_users):
            data = r.get(url, params={'access_token': token, 'v': '5.131',
                                    'user_ids': self.users[i],
                                    'fields': utils.FIELDS}).json()['response'][0]
            print(f'done {i}/{n_users}')
            user = {
                'id':            self.users[i],
                'age':           utils.get_age(data.get('bdate', False)),
                'occupation':    utils.get_occupation_type(data.get('occupation', False)),
                'sex':           utils.get_sex(data.get('sex', False)),
                'group':         self.group,
                'n_relatives':   utils.get_relatives_number(data.get('connections', False)),
                'relation':      utils.get_relation(data.get('relation', False))[0],
                'relation_type': utils.get_relation(data.get('relation', False))[1]
            }

            if not utils.get_city(data.get('city', False)):
                user['city'] = utils.get_home_town(data.get('home_town', False))
            else:
                user['city'] = utils.get_city(data.get('city', False))
            
            self.df = self.df.append(user, ignore_index=True)
        print(self.df.head())

    def save_df(self, path: str = 'users.csv'):
        self.df.to_csv(path, index=False)


    def get_users(self):
        return self.users
        


if __name__ == '__main__':
    parser = Parser(token)
    parser.set_group(groups['svoe_rodnoe'])

    #parser.set_users([5267])
    parser.parse_users_from_group()
    print(len(parser.get_users()))
    parser.parse_user_info()
    parser.save_df()
