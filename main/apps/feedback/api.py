# coding: utf-8

from google.appengine.ext import ndb
from flask.ext import restful
import flask

from apps import auth
from core import api
from core import util
import models


class FeedbacksAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    feedback_dbs, next_cursor, prev_cursor = models.Feedback.get_dbs()
    return api.make_response(
        feedback_dbs, models.feedback_fields, next_cursor, prev_cursor)

  @auth.admin_required
  def delete(self):
    feedback_keys = util.param('feedback_keys', list)
    user_db_keys = [ndb.Key(urlsafe=k) for k in feedback_keys]
    util.delete_dbs(user_db_keys)
    return flask.jsonify({
        'result': feedback_keys,
        'status': 'success',
      })


class FeedbackAPI(restful.Resource):
  @auth.admin_required
  def get(self, key):
    feedback = ndb.Key(urlsafe=key).get()
    if not feedback:
      flask.abort(404)
    return api.make_response(feedback, models.feedback_fields)


API = [
    (FeedbacksAPI, '/api/v1/feedbacks/', 'api.feedbacks'),
    (FeedbackAPI, '/api/v1/feedback/<string:key>/', 'api.feedback'),
  ]
