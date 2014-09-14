# coding: utf-8
from apps.auth import helpers


NAME = 'yandex'

FIELDS = {
    helpers.get_consumer_key_field_name(NAME): 'App ID',
    helpers.get_consumer_secret_field_name(NAME): 'App Secret',
  }

OAUTH = {
    'base_url': 'https://login.yandex.ru/',
    'request_token_url': None,
    'access_token_url': 'https://oauth.yandex.com/token',
    'authorize_url': 'https://oauth.yandex.com/authorize',
    'access_token_method': 'POST',
  }

CONFIG = helpers.make_provider_config(
    NAME, FIELDS, OAUTH, icon_class='fa-question')
