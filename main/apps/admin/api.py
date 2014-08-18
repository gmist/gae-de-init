# coding: utf-8
from flask.ext import restful

from apps import auth
from core.api import helpers
import models


class ConfigAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    return helpers.make_response(
        models.Config.get_master_db(),
        models.config_fields
      )


API = [
    (ConfigAPI, '/api/v1/config/', 'api.config'),
  ]
