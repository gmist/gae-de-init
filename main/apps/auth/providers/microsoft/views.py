# coding: utf-8
import flask

from apps.auth import helpers
from apps.user import models
from .import CONFIG


provider = helpers.make_provider(CONFIG)
bp = helpers.make_provider_bp(provider.name, __name__)


@bp.route('/authorized/')
def authorized():
  response = provider.authorized_response()
  if response is None:
    return 'Access denied: error=%s error_description=%s' % (
        flask.request.args['error'],
        flask.request.args['error_description'],
      )
  flask.session['oauth_token'] = (response['access_token'], '')
  me = provider.get(
      'me',
      data={'access_token': response['access_token']},
      headers={'accept-encoding': 'identity'},
    ).data
  if me.get('error'):
    return 'Unknown error: error:%s error_description:%s' % (
        me['code'],
        me['message'],
      )
  user_db = retrieve_user_from_microsoft(me)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_microsoft_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  return helpers.signin(provider)


def retrieve_user_from_microsoft(response):
  auth_id = '%s_%s' % (provider.name, response['id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  email = response['emails']['preferred'] or response['emails']['account']
  return helpers.create_user_db(
      auth_id=auth_id,
      name=response['name'] or '',
      username=email,
      email=email,
      verified=bool(email)
    )
