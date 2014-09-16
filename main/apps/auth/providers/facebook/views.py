# coding: utf-8
import flask

from apps.auth import helpers
from apps.user import models
from core import util
from .import CONFIG


PROVIDER_NAME = CONFIG['name']
bp = helpers.make_provider_bp(PROVIDER_NAME, __name__)
provider = helpers.make_provider(CONFIG)


@bp.route('/authorized/')
def authorized():
  resp = provider.authorized_response()
  if resp is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (resp['access_token'], '')
  me = provider.get('/me')
  user_db = retrieve_user_from_facebook(me.data)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_facebook_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  return helpers.signin(provider)


def retrieve_user_from_facebook(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  return helpers.create_user_db(
      auth_id,
      response['name'],
      response.get('username', response['name']),
      response.get('email', ''),
      verified=bool(response.get('email', ''))
    )
