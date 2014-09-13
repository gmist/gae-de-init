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
    base_url='https://api.stackexchange.com/2.1/',
    request_token_url=None,
    access_token_url='https://stackexchange.com/oauth/access_token',
    access_token_method='POST',
    authorize_url='https://stackexchange.com/oauth',
    consumer_key=PROVIDERS_DB.get_field('%s_client_id' % PROVIDER_NAME),
    consumer_secret=PROVIDERS_DB.get_field('%s_client_secret' % PROVIDER_NAME),
    request_token_params={},
  )

provider = provider_oauth.remote_app(PROVIDER_NAME, app_key=PROVIDER_KEY)
provider_oauth.init_app(app)


@bp.route('/authorized/')
@provider.authorized_handler
def authorized(resp):
  if resp is None:
    return 'Access denied: error=%s error_description=%s' % (
        flask.request.args['error'],
        flask.request.args['error_description'],
      )
  flask.session['oauth_token'] = (resp['access_token'], '')
  me = provider.get(
      'me',
      data={
          'site': 'stackoverflow',
          'access_token': resp['access_token'],
          'key': PROVIDERS_DB.get_field('%s_key' % PROVIDER_NAME),
        }
    )
  if me.data.get('error_id'):
    return 'Error: error_id=%s error_name=%s error_description=%s' % (
        me.data['error_id'],
        me.data['error_name'],
        me.data['error_message'],
      )
  if not me.data.get('items') or not me.data['items'][0]:
    return 'Unknown error, invalid server response: %s' % me.data
  user_db = retrieve_user_from_stackoverflow(me.data['items'][0])
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_stackoverflow_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  flask.session['oauth_token'] = None
  helpers.save_request_params()
  return provider.authorize(callback=flask.url_for(
      'auth.p.%s.authorized' % PROVIDER_NAME, _external=True
    ))


def retrieve_user_from_stackoverflow(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['user_id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  return helpers.create_user_db(
      auth_id,
      response['display_name'],
      response['display_name']
    )
