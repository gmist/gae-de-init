# coding: utf-8

import copy
from flask.ext import restful

from apps import auth
from core import util
import models


class AuthProvidersAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    auth_db = models.AuthProviders.get_master_db()
    auth_providers_config = copy.deepcopy(auth.PROVIDERS_CONFIG.values())
    auth_providers_config = sorted(auth_providers_config, key=lambda x: x.get('name'))
    fields = set()
    for provider in auth_providers_config:
      for field in provider.get('key_fields', {}).iterkeys():
        try:
          getattr(auth_db, field)
          fields.add(field)
        except AttributeError:
          pass
    auth_db._PROPERTIES = auth_db._PROPERTIES.union(fields)
    return util.jsonify_model_db(auth_db)


API = [
    (AuthProvidersAPI, '/api/v1/auth/providers/', 'api.auth.providers')
  ]
