# coding: utf-8
from flask.ext.oauthlib import client as oauth
import flask

from app import app
from apps.auth import helpers
from apps.auth.models import AuthProviders
from apps.user import models
from .import CONFIG


PROVIDERS_DB = AuthProviders.get_master_db()
PROVIDER_NAME = CONFIG['name']
PROVIDER_KEY = 'OAUTH_%s' % PROVIDER_NAME


bp = helpers.make_provider_bp(PROVIDER_NAME, __name__)
provider_oauth = oauth.OAuth()

app.config[PROVIDER_KEY] = dict(
    base_url='https://api.bitbucket.org/1.0/',
    request_token_url='https://bitbucket.org/!api/1.0/oauth/request_token',
    access_token_url='https://bitbucket.org/!api/1.0/oauth/access_token',
    authorize_url='https://bitbucket.org/!api/1.0/oauth/authenticate',
    consumer_key=PROVIDERS_DB.get_field('%s_key' % PROVIDER_NAME),
    consumer_secret=PROVIDERS_DB.get_field('%s_secret' % PROVIDER_NAME),
  )

provider = provider_oauth.remote_app(PROVIDER_NAME, app_key=PROVIDER_KEY)
provider_oauth.init_app(app)


@bp.route('/authorized/')
@provider.authorized_handler
def authorized(resp):
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
