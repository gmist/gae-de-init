# coding: utf-8
from flask.ext import oauth
import flask

from apps.auth import helpers
from apps.auth.models import AuthProviders
from apps.user import models
from core import util
from .import CONFIG


PROVIDERS_DB = AuthProviders.get_master_db()
PROVIDER_NAME = CONFIG['name']

bp = helpers.make_provider_bp(PROVIDER_NAME, __name__)
yahoo_oauth = oauth.OAuth()

yahoo = yahoo_oauth.remote_app(
    PROVIDER_NAME,
    base_url='https://social.yahooapis.com/',
    request_token_url='https://api.login.yahoo.com/oauth/v2/get_request_token',
    access_token_url='https://api.login.yahoo.com/oauth/v2/get_token',
    authorize_url='https://api.login.yahoo.com/oauth/v2/request_auth',
    consumer_key=PROVIDERS_DB.get_field('%s_consumer_key' % PROVIDER_NAME),
    consumer_secret=PROVIDERS_DB.get_field('%s_consumer_secret' % PROVIDER_NAME),
  )


@bp.route('/authorized/')
@yahoo.authorized_handler
def authorized(resp):
  if resp is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (
      resp['oauth_token'],
      resp['oauth_token_secret'],
    )

  try:
    yahoo_guid = yahoo.get(
        '/v1/me/guid', data={'format': 'json', 'realm': 'yahooapis.com'}
      ).data['guid']['value']

    profile = yahoo.get(
        '/v1/user/%s/profile' % yahoo_guid,
        data={'format': 'json', 'realm': 'yahooapis.com'}
      ).data['profile']
  except:
    flask.flash(
        'Something went wrong with Yahoo! sign in. Please try again.',
        category='danger',
      )
    return flask.redirect(util.get_next_url())
  user_db = retrieve_user_from_yahoo(profile)
  return helpers.signin_user_db(user_db)


@yahoo.tokengetter
def get_yahoo_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  helpers.save_request_params()
  flask.session.pop('oauth_token', None)
  try:
    return yahoo.authorize(
        callback=flask.url_for('auth.p.%s.authorized' % PROVIDER_NAME)
      )
  except:
    flask.flash(
        'Something went wrong with Yahoo! sign in. Please try again.',
        category='danger',
      )
    return flask.redirect(flask.url_for('auth.signin', next=util.get_next_url()))


def retrieve_user_from_yahoo(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['guid'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  if response.get('givenName') or response.get('familyName'):
    user_name = ' '.join((response['givenName'], response['familyName'])).strip()
  else:
    user_name = response['nickname']
  emails = [
      email for email in response.get('emails', []) if email.get('handle')]
  emails.sort(key=lambda e: e.get('primary', False))
  return helpers.create_user_db(
      auth_id,
      user_name,
      user_name,
      emails[0]['handle'] if emails else ''
    )
