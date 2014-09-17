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
  flask.session['oauth_token'] = (resp['access_token'], '')
  me = provider.get('account/info')
  user_db = retrieve_user_from_dropbox(me.data)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_dropbox_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  return helpers.signin(provider, scheme='https')


def retrieve_user_from_dropbox(response):
  auth_id = '%s_%s' % (provider.name, response['uid'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  return helpers.create_user_db(
      auth_id=auth_id,
      name=response['display_name'],
      username=response['display_name'],
    )
