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

  flask.session['oauth_token'] = (
      resp['oauth_token'],
      resp['oauth_token_secret'],
    )
  user_db = retrieve_user_from_twitter(resp)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_twitter_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  flask.session.pop('oauth_token', None)
  helpers.save_request_params()
  try:
    return provider.authorize(
        callback=flask.url_for('auth.p.%s.authorized' % PROVIDER_NAME)
      )
  except:
    flask.flash(
        'Something went wrong with Twitter sign in. Please try again.',
        category='danger',
      )
    return flask.redirect(
        flask.url_for('auth.signin', next=util.get_next_url())
      )


def retrieve_user_from_twitter(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['user_id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  return helpers.create_user_db(
      auth_id,
      response['screen_name'],
      response['screen_name'],
    )
