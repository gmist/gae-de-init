# coding: utf-8
import re
import flask

from apps.auth import helpers
from apps.user import models
from .import CONFIG


PROVIDER_NAME = CONFIG['name']
bp = helpers.make_provider_bp(PROVIDER_NAME, __name__)
provider = helpers.make_provider(CONFIG)


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
  flask.session['oauth_token'] = None
  helpers.save_request_params()
  return provider.authorize(callback=re.sub(r'^http:', 'https:', flask.url_for(
      'auth.p.%s.authorized' % PROVIDER_NAME, _external=True
    )))


def retrieve_user_from_dropbox(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['uid'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  return helpers.create_user_db(
      auth_id,
      response['display_name'],
      response['display_name'],
    )
