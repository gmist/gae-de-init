# coding: utf-8
from google.appengine.ext import ndb
from flask.ext import restful
import flask

from apps import auth
from core import api
from core import util
import models


class UsersAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    user_keys = util.param('user_keys', list)
    if user_keys:
      user_db_keys = [ndb.Key(urlsafe=k) for k in user_keys]
      user_dbs = ndb.get_multi(user_db_keys)
      return api.make_response(user_dbs, models.user_fields)

    user_dbs, next_cursor = models.User.get_dbs()
    return api.make_response(user_dbs, models.user_fields, next_cursor)

  @auth.admin_required
  def delete(self):
    user_keys = util.param('user_keys', list)
    if user_keys:
      user_db_keys = [ndb.Key(urlsafe=k) for k in user_keys]
      delete_user_dbs(user_db_keys)
      return flask.jsonify({
          'result': user_keys,
          'status': 'success',
        })
    return flask.jsonify({
        'result': 'User(s) %s not found' % user_keys,
        'status': 'fail',
      })


class UserAPI(restful.Resource):
  @auth.admin_required
  def get(self, key):
    user_db = ndb.Key(urlsafe=key).get()
    if not user_db:
      flask.abort(404)
    return api.make_response(user_db, models.user_fields)

  @auth.admin_required
  def delete(self, key):
    user_db = ndb.Key(urlsafe=key).get()
    if user_db:
      user_db.key.delete()
      return flask.jsonify({
          'result': key,
          'status': 'success',
        })
    return flask.jsonify({
        'result': 'User %s not found' % key,
        'status': 'fail',
    })


@ndb.transactional(xg=True)
def delete_user_dbs(user_db_keys):
  ndb.delete_multi(user_db_keys)


API = [
    (UsersAPI, '/api/v1/users/', 'api.users'),
    (UserAPI, '/api/v1/user/<string:key>/', 'api.user'),
  ]
