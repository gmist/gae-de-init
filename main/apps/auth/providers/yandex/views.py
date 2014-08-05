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

provider_oauth = oauth.OAuth()

provider = provider_oauth.remote_app(
    PROVIDER_NAME,
    base_url='https://login.yandex.ru/',
    request_token_url=None,
    access_token_url='https://oauth.yandex.com/token',
    authorize_url='https://oauth.yandex.com/authorize',
    access_token_method='POST',
    access_token_params={'grant_type': 'authorization_code'},
    consumer_key=PROVIDERS_DB.get_field('%s_app_id' % PROVIDER_NAME),
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
  access_token = resp['access_token']
  flask.session['oauth_token'] = (access_token, '')
  me = provider.get(
      '/info', data={'access_token': access_token, 'format': 'json'}
    )
  user_db = retrieve_user_from_yandex(me.data)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_yandex_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/%s/' % PROVIDER_NAME)
def signin():
  helpers.save_request_params()
  return provider.authorize(callback=flask.url_for(
      'auth.%s.service.authorized' % PROVIDER_NAME, _external=True
    ))


def retrieve_user_from_yandex(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
      return user_db
  return helpers.create_user_db(
      auth_id,
      response.get('real_name') or response.get('display_name'),
      response.get('display_name'),
      response.get('default_email' or response.get('emails', [''])[0]),
    )
