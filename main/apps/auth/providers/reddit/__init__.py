# coding: utf-8
from apps.auth import helpers
from core import util


NAME = 'reddit'

FIELDS = {
    helpers.get_consumer_key_field_name(NAME): 'Client ID',
    helpers.get_consumer_secret_field_name(NAME): 'Client Secret',
  }

OAUTH = {
    'base_url': 'https://oauth.reddit.com/api/v1/',
    'request_token_url': None,
    'access_token_url': 'https://ssl.reddit.com/api/v1/access_token',
    'access_token_method': 'POST',
    'access_token_params': {'grant_type': 'authorization_code'},
    'authorize_url': 'https://ssl.reddit.com/api/v1/authorize',
    'request_token_params': {'scope': 'identity', 'state': util.uuid()},
  }

CONFIG = helpers.make_provider_config(NAME, FIELDS, OAUTH)
