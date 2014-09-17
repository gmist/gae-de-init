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
  return helpers.signin(provider)


def retrieve_user_from_bitbucket(response):
  auth_id = '%s_%s' % (provider.name, response['username'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  if response['first_name'] or response['last_name']:
    name = ' '.join((response['first_name'], response['last_name'])).strip()
  else:
    name = response['username']
  emails = provider.get('users/%s/emails' % response['username'])
  email = ''.join([e['email'] for e in emails.data if e['primary']][0:1])
  return helpers.create_user_db(
      auth_id,
      name,
      response['username'],
      email=email,
      verified=bool(email),
    )
