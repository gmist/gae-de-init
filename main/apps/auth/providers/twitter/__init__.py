# coding: utf-8
from apps.auth import helpers


NAME = 'twitter'

FIELDS = {
    helpers.get_consumer_key_field_name(NAME): 'API key',
    helpers.get_consumer_secret_field_name(NAME): 'API secret',
  }

OAUTH = {
    'base_url': 'https://api.twitter.com/1.1/',
    'request_token_url': 'https://api.twitter.com/oauth/request_token',
    'access_token_url': 'https://api.twitter.com/oauth/access_token',
    'authorize_url': 'https://api.twitter.com/oauth/authorize',
  }

CONFIG = helpers.make_provider_config(NAME, FIELDS, OAUTH)
