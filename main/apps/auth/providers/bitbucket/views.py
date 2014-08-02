# coding: utf-8
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
bitbucket_oauth = oauth.OAuth()

bitbucket = bitbucket_oauth.remote_app(
    'bitbucket',
    base_url='https://api.bitbucket.org/1.0/',
    request_token_url='https://bitbucket.org/!api/1.0/oauth/request_token',
    access_token_url='https://bitbucket.org/!api/1.0/oauth/access_token',
    authorize_url='https://bitbucket.org/!api/1.0/oauth/authenticate',
    consumer_key=PROVIDERS_DB.get_field('%s_key' % PROVIDER_NAME),
    consumer_secret=PROVIDERS_DB.get_field('%s_secret' % PROVIDER_NAME),
  )


@bps.route('/oauth-authorized/')
@bitbucket.authorized_handler
def authorized(resp):
  if resp is None:
    return 'Access denied'
  flask.session['oauth_token'] = (
      resp['oauth_token'], resp['oauth_token_secret'],
    )
  me = bitbucket.get('user')
  user_db = retrieve_user_from_bitbucket(me.data['user'])
  return helpers.signin_user_db(user_db)


@bitbucket.tokengetter
def get_bitbucket_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/%s/' % PROVIDER_NAME)
def signin():
  flask.session['oauth_token'] = None
  helpers.save_request_params()
  return bitbucket.authorize(callback=flask.url_for(
      'auth.%s.service.authorized' % PROVIDER_NAME, _external=True
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
