# coding: utf-8
from apps.auth import helpers


NAME = 'stackoverflow'

FIELDS = {
    helpers.get_consumer_key_field_name(NAME): 'Client ID',
    helpers.get_consumer_secret_field_name(NAME): 'Client Secret',
    helpers.provider_field_name(NAME, 'key'): 'Key',
  }

OAUTH = {
    'base_url': 'https://api.stackexchange.com/2.1/',
    'request_token_url': None,
    'access_token_url': 'https://stackexchange.com/oauth/access_token',
    'access_token_method': 'POST',
    'authorize_url': 'https://stackexchange.com/oauth',
    'request_token_params': {},
  }

CONFIG = helpers.make_provider_config(
    NAME, FIELDS, OAUTH, title='Stack Overflow', icon_class='fa-stack-overflow')
