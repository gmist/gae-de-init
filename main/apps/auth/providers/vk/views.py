# coding: utf-8
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
  access_token = resp['access_token']
  flask.session['oauth_token'] = (access_token, '')
  me = provider.get('/method/getUserInfoEx', data={'access_token': access_token})
  user_db = retrieve_user_from_vk(me.data['response'])
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_vk_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  helpers.save_request_params()
  return provider.authorize(callback=flask.url_for(
      'auth.p.%s.authorized' % PROVIDER_NAME, _external=True
    ))


def retrieve_user_from_vk(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['user_id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  return helpers.create_user_db(
      auth_id,
      response['user_name'],
      response['user_name'],
    )
