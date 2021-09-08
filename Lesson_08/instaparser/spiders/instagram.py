from ..pass_data import PassData
import re
import scrapy
from scrapy.http import HtmlResponse
import json
from copy import deepcopy
from urllib.parse import urlencode
from ..items import InstaparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login_url = "https://www.instagram.com/accounts/login/ajax/"
    insta_login = PassData.get_login
    insta_pwd = PassData.get_password
    user_parse_account = 'vorobiov_ivan'
    posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'
    graph_url = '/graphql/query/'

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
            yield response.follow(f'/{self.user_parse_account}',
                                  callback=self.parse_user,
                                  cb_kwargs={'username': self.user_parse_account})

    def parse_user(self, response: HtmlResponse, username):
        user_id = self.get_user_id(response.text, username)
        variables = {"id": user_id, "first": 12}
        posts_url = f'{self.graph_url}?query_hash={self.posts_hash}&{urlencode(variables)}'

        yield response.follow(posts_url,
                              callback=self.user_data_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables)})

    def user_data_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info.get('end_cursor')
            posts_url = f'{self.graph_url}?query_hash={self.posts_hash}&{urlencode(variables)}'

            yield response.follow(posts_url,
                                  callback=self.user_data_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'variables': deepcopy(variables)})

        posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')
        for post in posts:
            item = InstaparserItem(
                username=username,
                user_id=user_id,
                photo=post.get('node').get('display_url'),
                likes=post.get('node').get('edge_media_preview_like').get('count'),
                post_data=post.get('node')
                )

            yield item

    @staticmethod
    def get_csrf_token(data):
        return re.findall('\"csrf_token\":\"\\w+"', data)[0].split(':')[1].replace('"', '')

    @staticmethod
    def get_user_id(data, username):
        matched = re.findall(f'{{\"id\":\"\\d+\",\"username\":\"{username}\"}}', data)
        return json.loads(matched[0]).get('id')
