# coding: utf-8

from google.appengine.ext import ndb
from flask.ext import restful
import flask

from apps import auth
from core import util
import models


class FeedbacksAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    feedback_dbs, feedback_cursor = models.Feedback.get_dbs()
    return util.jsonify_model_dbs(feedback_dbs, feedback_cursor)

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
    if feedback:
      return util.jsonify_model_db(feedback)
    return flask.jsonify({
        'result': 'Feedback %s not found',
        'status': 'fail',
    })


API = [
    (FeedbacksAPI, '/api/v1/feedbacks/', 'api.feedbacks'),
    (FeedbackAPI, '/api/v1/feedback/<string:key>/', 'api.feedback'),
  ]
