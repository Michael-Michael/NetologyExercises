# This program  works with vk.com user accounts
# It finds groups of user, in which there is none of his friends
# USER_ID contains vk.com id of target user
# To correct processing a valid access token need to be placed in TOKEN
# The results are displayed in the "secret_groups.json" file

from urllib.parse import urlencode
import requests
import time
import json
import os


USER_ID = 'tim_leary'

SERVICE_KEY = '11403f8811403f8811403f886f111d4ac51114011403f88483602710fc57cbbd4d427c2'
APP_ID = '6124877'
AUTHORIZE_URL = 'https://oauth.vk.com/authorize'
VERSION = '5.67'
VK_METHOD = 'https://api.vk.com/method/'

# auth_data = {
#     'client_id' : APP_ID,
#     'response_type': 'token',
#     'redirect_uri': 'https://oauth.vk.com/blank.html',
#     'scope' : 'friends, status, groups',
#     'v' : VERSION,
# }
# print('?'.join((AUTHORIZE_URL, urlencode(auth_data))))


TOKEN = '9b099950f58b0ded9ea7a701753b7172c0aa4986035aa270fa90095e0db750c5b178a3a767b4d766aeef1'


class Show:
    def __init__(self):
        self.points_num = 1
        self.total = 0

    def work(self):
        for i in range(self.points_num):
            print('.', end='')
        print()
        self.points_num = self.points_num % 10
        self.points_num = self.points_num + 1

    def counter(self, current):
        print('{} из {}'.format(current+1, self.total))


show = Show()
pool = requests.Session()


def make_request(method, add_params):
    params = {
        'v': VERSION,
        'access_token': TOKEN,
    }
    params.update(add_params)
    while True:
        show.work()
        response = pool.get(''.join((VK_METHOD, method)), params=params)
        try:
            if response.json()['error']['error_code'] == 6:
                time.sleep(0.3)
            elif response.json()['error']['error_code'] != 6:
                return None
        except KeyError:
            return response.json()


def friends_of(user_id, output='list'):
    params = {
        'user_id': user_id,
    }
    response = make_request('friends.get', params)
    if not response:
        return []
    if output == 'count':
        return response['response']['count']
    return response['response']['items']


def groups_of(user_id, output='list'):
    params = {
        'user_id': user_id,
        'count': '10',
    }
    response = make_request('groups.get', params)
    if output == 'count':
        return response['response']['count']
    return response['response']['items']


def unique_groups_of(user_id):
    unique_groups_of_user_ids = set(groups_of(user_id))
    show.total = int(friends_of(user_id, output='count'))
    user_friends_ids = friends_of(user_id)
    for i, friend_id in enumerate(user_friends_ids):
        show.counter(i)
        if get_users(friend_id)[0].get('deactivated'):
            continue
        groups_of_friend_ids = set(groups_of(friend_id))
        unique_groups_of_user_ids -= groups_of_friend_ids
        if not unique_groups_of_user_ids:
            break
    return unique_groups_of_user_ids


def get_users(user_ids, name_case='nom'):
    params = {
        'user_ids': user_ids,
        'name_case': name_case,
    }
    return make_request('users.get', params)["response"]


def get_group(group_id):
    params = {
        'group_ids': group_id,
        'fields': [
            'members_count',
        ],
    }
    return make_request('groups.getById', params)['response']


def main():
    user = get_users(USER_ID)[0]
    user_name = '{} {}'.format(user['first_name'], user['last_name'])
    print('Количество групп, в которых состоит {} - {}.'.format(
                                            user_name, groups_of(user['id'], 'count')))
    print('Группы, в которых нет ни одного из его друзей:')
    unique_groups_ids = unique_groups_of(user['id'])
    with open(os.path.join(os.getcwd(), 'secret_groups.json'), 'w+', encoding='utf-8') as f:
        for group_id in unique_groups_ids:
            group = (get_group(group_id))
            print('Id: {}  название: {}  количество участников: {}'.format(
                                                group[0]['id'], group[0]['name'], group[0]['members_count']))
            json.dump(group, f, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
