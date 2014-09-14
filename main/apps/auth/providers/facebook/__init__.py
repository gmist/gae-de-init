# coding: utf-8
from apps.auth import helpers


NAME = 'facebook'

FIELDS = {
    helpers.provider_field_name(NAME, 'consumer_key'): 'App ID',
    helpers.provider_field_name(NAME, 'consumer_secret'): 'App Secret',
  }

OAUTH = {
    'base_url': 'https://graph.facebook.com/',
    'request_token_url': None,
    'access_token_url': '/oauth/access_token',
    'authorize_url': 'https://www.facebook.com/dialog/oauth',
    'request_token_params': {'scope': 'email'},
  }

CONFIG = helpers.make_provider_config(NAME, FIELDS, OAUTH)
