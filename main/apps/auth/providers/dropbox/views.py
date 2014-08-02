# coding: utf-8
import re
from flask.ext import oauth
import flask

from apps.auth import helpers
from apps.auth.models import AuthProviders
from apps.user import models
from .import CONFIG

PROVIDERS_DB = AuthProviders.get_master_db()
PROVIDER_NAME = CONFIG['name']

bp = flask.Blueprint(
    'auth.%s' % PROVIDER_NAME,
    __name__,
    url_prefix='/auth',
    template_folder='templates',
  )

bps = flask.Blueprint(
    'auth.%s.service' % PROVIDER_NAME,
    __name__,
    url_prefix='/_s/callback/%s' % PROVIDER_NAME,
  )

provider_oauth = oauth.OAuth()

provider = provider_oauth.remote_app(
    PROVIDER_NAME,
    base_url='https://api.dropbox.com/1/',
    request_token_url=None,
    access_token_url='https://api.dropbox.com/1/oauth2/token',
    access_token_method='POST',
    access_token_params={'grant_type': 'authorization_code'},
    authorize_url='https://www.dropbox.com/1/oauth2/authorize',
    consumer_key=PROVIDERS_DB.get_field('%s_app_key' % PROVIDER_NAME),
    consumer_secret=PROVIDERS_DB.get_field('%s_app_secret' % PROVIDER_NAME),
  )


@bps.route('/oauth-authorized/')
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


@bp.route('/signin/%s/' % PROVIDER_NAME)
def signin():
  flask.session['oauth_token'] = None
  helpers.save_request_params()
  return provider.authorize(callback=re.sub(r'^http:', 'https:', flask.url_for(
      'auth.%s.service.authorized' % PROVIDER_NAME, _external=True
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
