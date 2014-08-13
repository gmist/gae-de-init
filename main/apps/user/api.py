# coding: utf-8
from datetime import datetime
from google.appengine.ext import ndb
from flask.ext import restful
import flask

from apps import auth
from core import util
import models


class UsersAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    user_keys = util.param('user_keys', list)
    if user_keys:
      user_db_keys = [ndb.Key(urlsafe=k) for k in user_keys]
      user_dbs = ndb.get_multi(user_db_keys)
      return util.jsonify_model_dbs(user_dbs)

    user_dbs, next_cursor = models.User.get_dbs()
    response_object = {
        'status': 'success',
        'count': len(user_dbs),
        'now': datetime.utcnow().isoformat(),
        'result': map(lambda l: restful.marshal(l, models.user_fields), user_dbs),
      }
    if next_cursor:
      response_object['next_cursor'] = next_cursor
      response_object['next_url'] = util.generate_next_url(next_cursor)
    return response_object

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
    return {
        'status': 'success',
        'now': datetime.utcnow().isoformat(),
        'result': restful.marshal(user_db, models.user_fields)
      }

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
