# coding: utf-8
from apps.auth import helpers

NAME = 'odnoklassniki'

FIELDS = {
    helpers.get_consumer_key_field_name(NAME): 'Client ID',
    helpers.get_consumer_secret_field_name(NAME): 'Client Secret',
    helpers.provider_field_name(NAME, 'consumer_public'): 'Consumer Public',
  }

OAUTH = {
    'base_url': 'http://api.odnoklassniki.ru/',
    'request_token_url': None,
    'access_token_url': 'http://api.odnoklassniki.ru/oauth/token.do',
    'authorize_url': 'http://www.odnoklassniki.ru/oauth/authorize',
    'access_token_params': {'grant_type': 'authorization_code'},
    'access_token_method': 'POST',
}

CONFIG = helpers.make_provider_config(
    NAME, FIELDS, OAUTH, icon_class='fa-question'
  )
