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
  resp = provider.authorized_response()
  if resp is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (
      resp['oauth_token'],
      resp['oauth_token_secret'],
    )

  try:
    yahoo_guid = provider.get(
        '/v1/me/guid',
        data={'format': 'json', 'realm': 'yahooapis.com'}
      ).data['guid']['value']

    profile = provider.get(
        '/v1/user/%s/profile' % yahoo_guid,
        data={'format': 'json', 'realm': 'yahooapis.com'}
      ).data['profile']
  except:
    flask.flash(
        u'Something went wrong with Yahoo! sign in. Please try again.',
        category='danger',
      )
    return flask.redirect(util.get_next_url())
  user_db = retrieve_user_from_yahoo(profile)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_yahoo_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  try:
    return helpers.signin(provider)
  except:
    flask.flash(
        u'Something went wrong with Yahoo! sign in. Please try again.',
        category='danger',
      )
    return flask.redirect(flask.url_for('auth.signin', next=util.get_next_url()))


def retrieve_user_from_yahoo(response):
  auth_id = '%s_%s' % (provider.name, response['guid'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  emails = [e for e in response.get('emails', []) if e.get('handle')]
  emails.sort(key=lambda e: e.get('primary', False))
  email = emails[0]['handle'] if emails else ''
  names = [response.get('givenName', ''), response.get('familyName', '')]
  return helpers.create_user_db(
      auth_id=auth_id,
      name=' '.join(names).strip() or response['nickname'],
      username=response['nickname'],
      email=email,
      verified=bool(email),
    )
