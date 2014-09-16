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
    return 'Access denied'
  flask.session['oauth_token'] = (
      resp['oauth_token'], resp['oauth_token_secret'],
    )
  me = provider.get('user')
  user_db = retrieve_user_from_bitbucket(me.data['user'])
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_bitbucket_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  flask.session['oauth_token'] = None
  helpers.save_request_params()
  return provider.authorize(callback=flask.url_for(
      'auth.p.%s.authorized' % PROVIDER_NAME, _external=True
    ))


def retrieve_user_from_bitbucket(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['username'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  if response['first_name'] or response['last_name']:
    name = ' '.join((response['first_name'], response['last_name'])).strip()
  else:
    name = response['username']
  return helpers.create_user_db(auth_id, name, response['username'])
