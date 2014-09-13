# coding: utf-8
from flask.ext.oauthlib import client as oauth
import flask

from app import app
from apps.auth import helpers
from apps.auth.models import AuthProviders
from apps.user import models
from core import util
from .import CONFIG


PROVIDERS_DB = AuthProviders.get_master_db()
PROVIDER_NAME = CONFIG['name']
PROVIDER_KEY = 'OAUTH_%s' % PROVIDER_NAME

bp = helpers.make_provider_bp(PROVIDER_NAME, __name__)
provider_oauth = oauth.OAuth()

app.config[PROVIDER_KEY] = dict(
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=PROVIDERS_DB.get_field('%s_consumer_key' % PROVIDER_NAME),
    consumer_secret=PROVIDERS_DB.get_field('%s_consumer_secret' % PROVIDER_NAME),
  )

provider = provider_oauth.remote_app(PROVIDER_NAME, app_key=PROVIDER_KEY)
provider_oauth.init_app(app)


@bp.route('/authorized/')
@provider.authorized_handler
def authorized(resp):
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
