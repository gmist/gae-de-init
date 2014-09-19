# coding: utf-8
import flask

from apps.auth import helpers
from apps.user import models
from core import util
from .import CONFIG


provider = helpers.make_provider(CONFIG)
bp = helpers.make_provider_bp(provider.name, __name__)


@bp.route('/authorized/')
def authorized():
  response = provider.authorized_response()
  if response is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (
      response['oauth_token'],
      response['oauth_token_secret'],
    )
  user_db = retrieve_user_from_twitter(response)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_twitter_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  try:
    return helpers.signin(provider)
  except:
    flask.flash(
        u'Something went wrong with Twitter sign in. Please try again.',
        category='danger',
      )
    return flask.redirect(
        flask.url_for('auth.signin', next=util.get_next_url())
      )


def retrieve_user_from_twitter(response):
  auth_id = '%s_%s' % (provider.name, response['user_id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  return helpers.create_user_db(
      auth_id=auth_id,
      name=response['screen_name'],
      username=response['screen_name'],
    )
