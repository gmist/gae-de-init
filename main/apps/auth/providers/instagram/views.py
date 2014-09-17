# coding: utf-8
import flask

from apps.auth import helpers
from apps.user import models
from .import CONFIG


provider = helpers.make_provider(CONFIG)
bp = helpers.make_provider_bp(provider.name, __name__)


@bp.route('/authorized/')
def authorized():
  resp = provider.authorized_response()
  if resp is None:
    return 'Access denied: error=%s error_description=%s' % (
        flask.request.args['error'],
        flask.request.args['error_description'],
      )
  access_token = resp['access_token']
  flask.session['oauth_token'] = (access_token, '')
  me = resp['user']
  user_db = retrieve_user_from_instagram(me)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_instagram_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/%s/' % provider.name)
def signin():
  return helpers.signin(provider)


def retrieve_user_from_instagram(response):
  auth_id = '%s_%s' % (provider.name, response['id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  return helpers.create_user_db(
      auth_id,
      response['full_name'] or response['username'],
      response['username'],
    )
