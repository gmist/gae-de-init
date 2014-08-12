# coding: utf-8

from google.appengine.ext import ndb
from flask.ext import restful
import flask

from core import util
from apps.auth import admin_required
import models


class UsersAPI(restful.Resource):
  @admin_required
  def get(self):
    user_keys = util.param('user_keys', list)
    if user_keys:
      user_db_keys = [ndb.Key(urlsafe=k) for k in user_keys]
      user_dbs = ndb.get_multi(user_db_keys)
    else:
      user_dbs, _ = models.User.get_dbs()
    return util.jsonify_model_dbs(user_dbs)

  @admin_required
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
  @admin_required
  def get(self, key):
    user_db = ndb.Key(urlsafe=key).get()
    return util.jsonify_model_db(user_db)

  @admin_required
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
