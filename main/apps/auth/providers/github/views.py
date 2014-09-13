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
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    consumer_key=PROVIDERS_DB.get_field('%s_client_id' % PROVIDER_NAME),
    consumer_secret=PROVIDERS_DB.get_field('%s_client_secret' % PROVIDER_NAME),
    request_token_params={'scope': 'user:email'},
  )

provider = provider_oauth.remote_app(PROVIDER_NAME, app_key=PROVIDER_KEY)
provider_oauth.init_app(app)


@bp.route('/oauth-authorized/')
@provider.authorized_handler
def authorized(resp):
  if resp is None:
    return 'Access denied: error=%s' % flask.request.args['error']
  flask.session['oauth_token'] = (resp['access_token'], '')
  me = provider.get('user')
  user_db = retrieve_user_from_github(me.data)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_github_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  helpers.save_request_params()
  return provider.authorize(callback=flask.url_for(
      'auth.p.%s.authorized' % PROVIDER_NAME, _external=True
    ))


def retrieve_user_from_github(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, str(response['id']))
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  return helpers.create_user_db(
      auth_id,
      response.get('name', response.get('login')),
      response.get('login'),
      response.get('email', ''),
      verified=bool(response.get('email', ''))
    )
