# coding: utf-8
from apps.auth import helpers


NAME = 'github'

FIELDS = {
    helpers.provider_field_name(NAME, 'consumer_key'): 'Client ID',
    helpers.provider_field_name(NAME, 'consumer_secret'): 'Client Secret',
  }

OAUTH = {
    'base_url': 'https://api.github.com/',
    'request_token_url': None,
    'access_token_url': 'https://github.com/login/oauth/access_token',
    'authorize_url': 'https://github.com/login/oauth/authorize',
    'request_token_params': {'scope': 'user:email'},
  }

CONFIG = helpers.make_provider_config(NAME, FIELDS, OAUTH, 'GitHub')
