# coding: utf-8
from apps.auth import helpers


NAME = 'bitbucket'

FIELDS = {
    helpers.provider_field_name(NAME, 'consumer_key'): 'Key',
    helpers.provider_field_name(NAME, 'consumer_secret'): 'Secret',
  }

OAUTH = {
    'base_url': 'https://api.bitbucket.org/1.0/',
    'request_token_url': 'https://bitbucket.org/!api/1.0/oauth/request_token',
    'access_token_url': 'https://bitbucket.org/!api/1.0/oauth/access_token',
    'authorize_url': 'https://bitbucket.org/!api/1.0/oauth/authenticate',
  }

CONFIG = helpers.make_provider_config(NAME, FIELDS, OAUTH)
