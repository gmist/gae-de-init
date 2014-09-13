# coding: utf-8
import re
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
    base_url='https://api.dropbox.com/1/',
    request_token_url=None,
    access_token_url='https://api.dropbox.com/1/oauth2/token',
    access_token_method='POST',
    access_token_params={'grant_type': 'authorization_code'},
    authorize_url='https://www.dropbox.com/1/oauth2/authorize',
    consumer_key=PROVIDERS_DB.get_field('%s_app_key' % PROVIDER_NAME),
    consumer_secret=PROVIDERS_DB.get_field('%s_app_secret' % PROVIDER_NAME),
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
      'account/info',
      headers={'Authorization': 'Bearer %s' % resp['access_token']}
    )
  user_db = retrieve_user_from_dropbox(me.data)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_dropbox_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  flask.session['oauth_token'] = None
  helpers.save_request_params()
  return provider.authorize(callback=re.sub(r'^http:', 'https:', flask.url_for(
      'auth.p.%s.authorized' % PROVIDER_NAME, _external=True
    )))


def retrieve_user_from_dropbox(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['uid'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  return helpers.create_user_db(
      auth_id,
      response['display_name'],
      response['display_name'],
    )
