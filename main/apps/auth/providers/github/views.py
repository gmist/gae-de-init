# coding: utf-8
import flask

from apps.auth import helpers
from apps.user import models
from .import CONFIG


provider = helpers.make_provider(CONFIG)
bp = helpers.make_provider_bp(provider.name, __name__)


@bp.route('/oauth-authorized/')
def authorized():
  response = provider.authorized_response()
  if response is None:
    return 'Access denied: error=%s' % flask.request.args['error']
  flask.session['oauth_token'] = (response['access_token'], '')
  me = provider.get('user')
  user_db = retrieve_user_from_github(me.data)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_github_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  return helpers.signin(provider)


def retrieve_user_from_github(response):
  auth_id = '%s_%s' % (provider.name, str(response['id']))
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  return helpers.create_user_db(
      auth_id=auth_id,
      name=response.get('name', response.get('login')),
      username=response.get('login'),
      email=response.get('email', ''),
      verified=bool(response.get('email', ''))
    )
