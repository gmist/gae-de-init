# coding: utf-8
from apps.auth import helpers
from core import util


NAME = 'linkedin'

FIELDS = {
    helpers.get_consumer_key_field_name(NAME): 'API Key',
    helpers.get_consumer_secret_field_name(NAME): 'Secret Key',
  }

OAUTH = {
    'base_url': 'https://api.linkedin.com/v1/',
    'request_token_url': None,
    'access_token_url': 'https://www.linkedin.com/uas/oauth2/accessToken',
    'access_token_method': 'POST',
    'authorize_url': 'https://www.linkedin.com/uas/oauth2/authorization',
    'request_token_params': {
        'scope': 'r_basicprofile r_emailaddress',
        'state': util.uuid(),
      },
  }

CONFIG = helpers.make_provider_config(NAME, FIELDS, OAUTH, 'LinkedIn')
