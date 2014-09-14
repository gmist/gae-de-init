# coding: utf-8
from apps.auth import helpers


NAME = 'instagram'

FIELDS = {
    helpers.provider_field_name(NAME, 'consumer_key'): 'Client ID',
    helpers.provider_field_name(NAME, 'consumer_secret'): 'Client Secret',
  }

OAUTH = {
    'base_url': 'https://api.instagram.com/v1',
    'request_token_url': None,
    'access_token_url': 'https://api.instagram.com/oauth/access_token',
    'access_token_params': {'grant_type': 'authorization_code'},
    'access_token_method': 'POST',
    'authorize_url': 'https://instagram.com/oauth/authorize/',
  }

CONFIG = helpers.make_provider_config(NAME, FIELDS, OAUTH)
