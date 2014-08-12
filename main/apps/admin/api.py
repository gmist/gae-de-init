# coding: utf-8

from flask.ext import restful

from core import util
from apps import auth
import models


class ConfigAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    config_db = models.Config.get_master_db()
    return util.jsonify_model_db(config_db)


API = [
    (ConfigAPI, '/api/v1/config/', 'api.config'),
  ]
