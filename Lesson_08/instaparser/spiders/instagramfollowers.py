from ..pass_data import PassData
import scrapy
from scrapy.http import HtmlResponse
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from ..items import InstaparserItem


class InstagramfollowersSpider(scrapy.Spider):
    pass_data = PassData()
    name = 'instagramfollowers'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    insta_login_url = "https://www.instagram.com/accounts/login/ajax/"
    insta_login = pass_data.get_login
    insta_pwd = pass_data.get_password
    user_parse_accounts_list = ['machine_learning_with_python', 'python.learning']
    posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'
    api_url = 'https://i.instagram.com/api/v1/'

    def parse(self, response: HtmlResponse):
        yield scrapy.FormRequest(self.insta_login_url,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.insta_login,
                                           'enc_password': self.insta_pwd},
                                 headers={'X-CSRFToken': self.get_csrf_token(response.text)})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            for user_parse_account in self.user_parse_accounts_list:
                yield response.follow(f'/{user_parse_account}',
                                      callback=self.parse_user,
                                      cb_kwargs={'username': user_parse_account})

    def parse_user(self, response: HtmlResponse, username):
        user_id = self.get_user_id(response.text, username)
        variables = {"count": 12}

        for user_status in ('following', 'followers'):
            get_follow_users_url = f'{self.api_url}friendships/{user_id}/{user_status}/?{urlencode(variables)}'
            yield response.follow(get_follow_users_url,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'variables': deepcopy(variables),
                                             'user_status': user_status},
                                  callback=self.parse_user_follow,
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})

    def parse_user_follow(self, response: HtmlResponse, username, user_id, variables, user_status):
        json_data = response.json()
        if json_data.get('next_max_id'):
            variables['max_id'] = json_data.get('next_max_id')
            get_following_users_url = f'{self.api_url}friendships/{user_id}/{user_status}/?{urlencode(variables)}'

            yield response.follow(get_following_users_url,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'variables': deepcopy(variables),
                                             'user_status': user_status},
                                  callback=self.parse_user_follow,
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})

        for user in json_data.get('users'):
            item = InstaparserItem(
                username=user.get('username'),
                user_status=user_status,
                user_id=user.get('pk'),
                photo=user.get('profile_pic_url'),
                from_username=username
            )

            yield item

    @staticmethod
    def get_csrf_token(data):
        return re.findall('\"csrf_token\":\"\\w+"', data)[0].split(':')[1].replace('"', '')

    @staticmethod
    def get_user_id(data, username):
        matched = re.findall(f'{{\"id\":\"\\d+\",\"username\":\"{username}\"}}', data)
        return json.loads(matched[0]).get('id')
