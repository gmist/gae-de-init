# coding: utf-8
import flask

from apps.auth import helpers
from apps.auth.models import AuthProviders
from apps.user import models
from .import CONFIG


PROVIDERS_DB = AuthProviders.get_master_db()
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
      data={
          'site': 'stackoverflow',
          'access_token': response['access_token'],
          'key': PROVIDERS_DB.get_field('%s_key' % provider.name),
        }
    )
  if me.data.get('error_id'):
    return 'Error: error_id=%s error_name=%s error_description=%s' % (
        me.data['error_id'],
        me.data['error_name'],
        me.data['error_message'],
      )
  if not me.data.get('items') or not me.data['items'][0]:
    return 'Unknown error, invalid server response: %s' % me.data
  user_db = retrieve_user_from_stackoverflow(me.data['items'][0])
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_stackoverflow_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  return helpers.signin(provider)


def retrieve_user_from_stackoverflow(response):
  auth_id = '%s_%s' % (provider.name, response['user_id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  return helpers.create_user_db(
      auth_id=auth_id,
      name=response['display_name'],
      username=response['display_name']
    )
