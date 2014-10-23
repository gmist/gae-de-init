# coding: utf-8
import flask

from apps.auth import helpers
from apps.user import models
from core import util
from .import CONFIG


provider = helpers.make_provider(CONFIG)
bp = helpers.make_provider_bp(provider.name, __name__)


def change_linkedin_query(uri, headers, body):
    auth = headers.pop('Authorization')
    headers['x-li-format'] = 'json'
    if auth:
        auth = auth.replace('Bearer', '').strip()
        if '?' in uri:
            uri += '&oauth2_access_token=' + auth
        else:
            uri += '?oauth2_access_token=' + auth
    return uri, headers, body

provider.pre_request = change_linkedin_query


@bp.route('/authorized/')
def authorized():
  response = provider.authorized_response()
  if response is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())
  flask.session['access_token'] = (response['access_token'], '')
  me = provider.get('people/~:(id,first-name,last-name,email-address)')
  user_db = retrieve_user_from_linkedin(me.data)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_linkedin_oauth_token():
  return flask.session.get('access_token')


@bp.route('/signin/%s/' % provider.name)
def signin():
  return helpers.signin(provider)


def retrieve_user_from_linkedin(response):
  auth_id = '%s_%s' % (provider.name, response['id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  names = [response.get('firstName', ''), response.get('lastName', '')]
  name = ' '.join(names).strip()
  email = response.get('emailAddress', '')
  return helpers.create_user_db(
      auth_id=auth_id,
      name=name,
      username=email or name,
      email=email,
      verified=bool(email),
    )

