from abc import ABC

import scrapy
from re import search
from scrapy.http import HtmlResponse
from instagramParser.items import InstagramParserItem
from config import get_config as cfg


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com', 'cdninstagram.com', 'fbcdn.net']
    start_urls = ['https://www.instagram.com/']
    inst_login_url = 'https://www.instagram.com/accounts/login/ajax/'

    def __init__(self, user='ai_machine_learning', **kwargs):
        super().__init__(**kwargs)
        self.parse_user = user
        self.inst_login = cfg['Instagram']['username']
        self.inst_pswd = cfg['Instagram']['enc_password']

        self.friendships = 'https://i.instagram.com/api/v1/friendships/'
        self.friendships_follow = '/api/v1/friendships/'
        self.followers = '/followers/?count=12&search_surface=follow_list_page'
        self.following = '/following/?count=12'

    def parse(self, response: HtmlResponse):
        # csrf = self.fetch_csrf_token(list(dict(response.headers)[b'Set-Cookie']))
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_url,
            method='POST',
            callback=self.login,
            formdata={
                'username': self.inst_login,
                'enc_password': self.inst_pswd},
            headers={'X-CSRFToken': csrf}
        )

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            yield response.follow(
                f'/{self.parse_user}',
                callback=self.parse_user_friendships,
                cb_kwargs={'username': self.parse_user}
            )

    def parse_user_friendships(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text)

        friendships_urls = [
            f"{self.friendships}{user_id}{self.followers}",
            f"{self.friendships}{user_id}{self.following}"
        ]
        for url in friendships_urls:
            yield scrapy.Request(url,
                                 callback=self.user_friendships_parse,
                                 cb_kwargs={'username': username,
                                            'user_id': user_id
                                            },
                                 headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                                 )

    def user_friendships_parse(self, response: HtmlResponse, username, user_id):
        j_data = dict(response.json())
        friendship_type = 'following' if response.url.find('following') >= 0 else 'follower'

        if j_data.get('big_list'):
            if friendship_type == 'following':
                url = f"{self.friendships}{user_id}{self.following}&max_id={j_data['next_max_id']}"
            else:
                url = f"{self.friendships}{user_id}{self.followers}&max_id={j_data['next_max_id']}"
            yield response.follow(url,
                                  callback=self.user_friendships_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id
                                             },
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                                  )

        users = j_data.get('users')
        for user in users:
            item = InstagramParserItem(
                username=username,
                user_id=user_id,
                friendship_type=friendship_type,
                friend_photo=user['profile_pic_url'],
                friend_pk=user['pk'],
                friend_login=user['username'],
                friend_has_anonymous_profile_picture=user['has_anonymous_profile_picture'],
                friend_data=user
            )
            yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        match = search(r'"csrf_token":"(\w+)"', text).groups()
        return match[0]
        # csrf = None
        # for cookie in cookies:
        #     cookie = cookie.decode('UTF-8')
        #     if cookie.find('csrf') >= 0:
        #         csrf = cookie.split('; ')[0].split('=')[1]
        # return csrf

    def fetch_user_id(self, html_text):
        match = search(r'"owner":{"id":"(\d+)","username":"%s"}' % self.parse_user, html_text).groups()
        return match[0]
