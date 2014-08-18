# coding: utf-8
import copy
from core.api.helpers import make_response
from flask.ext import restful
from flask.ext.restful import fields
import funcy

from apps import auth
from core import api
from core import base
import models


class AuthProvidersAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    auth_db = models.AuthProviders.get_master_db()
    auth_providers_config = copy.deepcopy(auth.PROVIDERS_CONFIG.values())
    auth_providers_config = sorted(auth_providers_config, key=lambda x: x.get('name'))
    provider_fields = {}
    for provider in auth_providers_config:
      for field in provider.get('key_fields', {}).iterkeys():
        try:
          getattr(auth_db, field)
          provider_fields[field] = fields.String
        except AttributeError:
          pass
    provider_fields = funcy.merge(base.base_fields, provider_fields)
    return make_response(auth_db, provider_fields)


API = [
    (AuthProvidersAPI, '/api/v1/auth/providers/', 'api.auth.providers')
  ]
