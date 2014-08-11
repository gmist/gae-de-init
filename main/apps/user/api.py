# coding: utf-8

from flask.ext import restful

from core import util
import models


class UserListAPI(restful.Resource):
  def get(self):
    user_dbs, _ = models.User.get_dbs()
    return util.jsonify_model_dbs(user_dbs)

  def post(self):
    pass


class UserAPI(restful.Resource):
  def get(self, uid):
    pass

  def put(self, uid):
    pass

  def delete(self, uid):
    pass


API = [
    [UserListAPI, '/api/v1/users/', 'api.users'],
    [UserAPI, '/api/v1/users/<int:uid>/', 'api.user'],
  ]
