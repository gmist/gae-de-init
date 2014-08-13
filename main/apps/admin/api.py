# coding: utf-8

from flask.ext import restful

from core import api
from apps import auth
import models


class ConfigAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    return api.make_response(models.Config.get_master_db(), models.config_fields)


API = [
    (ConfigAPI, '/api/v1/config/', 'api.config'),
  ]
