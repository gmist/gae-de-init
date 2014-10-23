# coding: utf-8
from apps.auth import helpers


NAME = 'yahoo'

FIELDS = {
    helpers.get_consumer_key_field_name(NAME): 'Consumer Key',
    helpers.get_consumer_secret_field_name(NAME): 'Consumer Secret',
  }

OAUTH = {
    'base_url': 'https://query.yahooapis.com/',
    'request_token_url': 'https://api.login.yahoo.com/oauth/v2/get_request_token',
    'access_token_url': 'https://api.login.yahoo.com/oauth/v2/get_token',
    'authorize_url': 'https://api.login.yahoo.com/oauth/v2/request_auth',
  }

CONFIG = helpers.make_provider_config(NAME, FIELDS, OAUTH, title='Yahoo!')
