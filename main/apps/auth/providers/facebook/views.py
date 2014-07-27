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
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=PROVIDERS_DB.get_field('%s_app_id' % PROVIDER_NAME),
    consumer_secret=PROVIDERS_DB.get_field('%s_app_secret' % PROVIDER_NAME),
    request_token_params={'scope': 'email'},
  )


@bps.route('/oauth-authorized/')
@provider.authorized_handler
def authorized(resp):
  if resp is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  flask.session['oauth_token'] = (resp['access_token'], '')
  me = provider.get('/me')
  user_db = retrieve_user_from_facebook(me.data)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_facebook_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/%s/' % PROVIDER_NAME)
def signin():
  helpers.save_request_params()
  return provider.authorize(callback=flask.url_for(
      'auth.%s.service.authorized' % PROVIDER_NAME, _external=True
    ))


def retrieve_user_from_facebook(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  return helpers.create_user_db(
      auth_id,
      response['name'],
      response['username'] if 'username' in response else response['id'],
      response['email'],
    )
