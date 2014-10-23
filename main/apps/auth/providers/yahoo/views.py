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
  fields = 'guid, emails, familyName, givenName, nickname'
  me = provider.get(
      '/v1/yql',
      data={
          'format': 'json',
          'q': 'select %s from social.profile where guid = me;' % fields,
          'realm': 'yahooapis.com',
        },
    )
  user_db = retrieve_user_from_yahoo(me.data['query']['results']['profile'])
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
  names = [response.get('givenName', ''), response.get('familyName', '')]
  emails = response.get('emails', {})
  if not isinstance(emails, list):
    emails = [emails]
  emails = [e for e in emails if 'handle' in e]
  emails.sort(key=lambda e: e.get('primary', False))
  email = emails[0]['handle'] if emails else ''
  return helpers.create_user_db(
      auth_id=auth_id,
      name=' '.join(names).strip() or response['nickname'],
      username=response['nickname'],
      email=email,
      verified=bool(email),
    )
