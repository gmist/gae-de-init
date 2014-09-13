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
    base_url='https://apis.live.net/v5.0/',
    request_token_url=None,
    access_token_url='https://login.live.com/oauth20_token.srf',
    access_token_method='POST',
    access_token_params={'grant_type': 'authorization_code'},
    authorize_url='https://login.live.com/oauth20_authorize.srf',
    consumer_key=PROVIDERS_DB.get_field('%s_client_id' % PROVIDER_NAME),
    consumer_secret=PROVIDERS_DB.get_field('%s_client_secret' % PROVIDER_NAME),
    request_token_params={'scope': 'wl.emails'},
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
      data={'access_token': resp['access_token']},
      headers={'accept-encoding': 'identity'},
    ).data
  if me.get('error'):
    return 'Unknown error: error:%s error_description:%s' % (
        me['code'],
        me['message'],
      )
  user_db = retrieve_user_from_microsoft(me)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_microsoft_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  helpers.save_request_params()
  return provider.authorize(callback=flask.url_for(
      'auth.p.%s.authorized' % PROVIDER_NAME, _external=True
    ))


def retrieve_user_from_microsoft(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  email = response['emails']['preferred'] or response['emails']['account']
  return helpers.create_user_db(
      auth_id,
      response['name'] or '',
      email,
      email,
      verified=bool(email)
    )
