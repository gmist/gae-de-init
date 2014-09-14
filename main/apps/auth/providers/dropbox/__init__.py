# coding: utf-8
from apps.auth import helpers


NAME = 'dropbox'

FIELDS = {
    helpers.provider_field_name(NAME, 'consumer_key'): 'App ID',
    helpers.provider_field_name(NAME, 'consumer_secret'): 'App Secret',
  }

OAUTH = {
    'base_url': 'https://api.dropbox.com/1/',
    'request_token_url': None,
    'access_token_url': 'https://api.dropbox.com/1/oauth2/token',
    'access_token_method': 'POST',
    'access_token_params': {'grant_type': 'authorization_code'},
    'authorize_url': 'https://www.dropbox.com/1/oauth2/authorize',
  }

CONFIG = helpers.make_provider_config(NAME, FIELDS, OAUTH)
