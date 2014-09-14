# coding: utf-8
from apps.auth import helpers


NAME = 'vk'

FIELDS = {
    helpers.get_consumer_key_field_name(NAME): 'App ID',
    helpers.get_consumer_secret_field_name(NAME): 'App Secret',
  }

OAUTH = {
    'base_url': 'https://api.vk.com/',
    'request_token_url': None,
    'access_token_url': 'https://oauth.vk.com/access_token',
    'authorize_url': 'https://oauth.vk.com/authorize',
  }

CONFIG = helpers.make_provider_config(NAME, FIELDS, OAUTH, title='VK')
