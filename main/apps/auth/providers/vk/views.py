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

vk_oauth = oauth.OAuth()

vk = vk_oauth.remote_app(
    'vk',
    base_url='https://api.vk.com/',
    request_token_url=None,
    access_token_url='https://oauth.vk.com/access_token',
    authorize_url='https://oauth.vk.com/authorize',
    consumer_key=PROVIDERS_DB.get_field('%s_app_id' % PROVIDER_NAME),
    consumer_secret=PROVIDERS_DB.get_field('%s_app_secret' % PROVIDER_NAME),
  )


@bps.route('/oauth-authorized/')
@vk.authorized_handler
def authorized(resp):
  if resp is None:
    return 'Access denied: error=%s error_description=%s' % (
        flask.request.args['error'],
        flask.request.args['error_description'],
      )
  access_token = resp['access_token']
  flask.session['oauth_token'] = (access_token, '')
  me = vk.get('/method/getUserInfoEx', data={'access_token': access_token})
  user_db = retrieve_user_from_vk(me.data['response'])
  return helpers.signin_user_db(user_db)


@vk.tokengetter
def get_vk_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/%s/' % PROVIDER_NAME)
def signin():
  helpers.save_request_params()
  return vk.authorize(callback=flask.url_for(
      'auth.vk.service.authorized', _external=True
    ))


def retrieve_user_from_vk(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['user_id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db

  return helpers.create_user_db(
      auth_id,
      response['user_name'],
      response['user_name'],
    )

