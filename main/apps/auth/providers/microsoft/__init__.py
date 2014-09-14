# coding: utf-8
from apps.auth import helpers


NAME = 'microsoft'

FIELDS = {
    helpers.get_consumer_key_field_name(NAME): 'Client ID',
    helpers.get_consumer_secret_field_name(NAME): 'Client Secret',
  }

OAUTH = {
    'base_url': 'https://apis.live.net/v5.0/',
    'request_token_url': None,
    'access_token_url': 'https://login.live.com/oauth20_token.srf',
    'access_token_method': 'POST',
    'authorize_url': 'https://login.live.com/oauth20_authorize.srf',
    'request_token_params': {'scope': 'wl.emails'},
  }

CONFIG = helpers.make_provider_config(
    NAME, FIELDS, OAUTH, icon_class='fa-windows'
  )
