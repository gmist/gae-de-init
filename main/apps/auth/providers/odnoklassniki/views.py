# coding: utf-8
import hashlib
import json
import urllib
import urllib2
from flask.ext import oauth
import flask

from apps.auth import helpers
from apps.auth.models import AuthProviders
from apps.user import models
from core import util
from .import CONFIG


PROVIDERS_DB = AuthProviders.get_master_db()
PROVIDER_NAME = CONFIG['name']

bp = helpers.make_provider_bp(PROVIDER_NAME, __name__)
provider_oauth = oauth.OAuth()

provider = provider_oauth.remote_app(
    PROVIDER_NAME,
    base_url='http://api.odnoklassniki.ru/',
    request_token_url=None,
    access_token_url='http://api.odnoklassniki.ru/oauth/token.do',
    authorize_url='http://www.odnoklassniki.ru/oauth/authorize',
    consumer_key=PROVIDERS_DB.get_field('%s_app_id' % PROVIDER_NAME),
    consumer_secret=PROVIDERS_DB.get_field('%s_app_secret' % PROVIDER_NAME),
    access_token_params={'grant_type': 'authorization_code'},
    access_token_method='POST',
  )


def odnoklassniki_oauth_sig(data, client_secret):
  suffix = hashlib.md5(
      '{0:s}{1:s}'.format(data['access_token'], client_secret)
    ).hexdigest()
  check_list = sorted([
      '{0:s}={1:s}'.format(key, value)
      for key, value in data.items()
      if key != 'access_token'
    ])
  return hashlib.md5(''.join(check_list) + suffix).hexdigest()


@bp.route('/authorized/')
@provider.authorized_handler
def authorized(resp):
  if resp is None:
    return 'Access denied: reason=%s error=%s' % (
        flask.request.args['error_reason'],
        flask.request.args['error_description']
      )
  access_token = resp.get('access_token')
  if not access_token:
    return 'Access denied: reason=%s error=%s' % (
        resp.get('error_description', 'Unknown'),
        resp.get('error', 'Unknown'),
      )
  flask.session['oauth_token'] = (access_token, '')
  try:
    data = {
        'method': 'users.getCurrentUser',
        'application_key':
        PROVIDERS_DB.get_field('%s_consumer_public' % PROVIDER_NAME),
        'access_token': access_token,
      }
    data['sig'] = odnoklassniki_oauth_sig(
        data, client_secret=provider.consumer_secret
      )
    params = urllib.urlencode(data)
    url = provider.base_url + 'fb.do'
    request = urllib2.Request(url, params)
    odnoklassniki_resp = json.loads(urllib2.urlopen(request).read())
    user_db = retrieve_user_from_odnoklassniki(odnoklassniki_resp)
  except:
    flask.flash(
        'Something went wrong with Odnoklassniki sign in. Please try again.',
        category='danger'
      )
    return flask.redirect(flask.url_for(
        'auth.signin', next=util.get_next_url())
      )
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_odnoklassniki_oauth_token():
    return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  helpers.save_request_params()
  return provider.authorize(
      callback=flask.url_for(
          'auth.p.%s.authorized' % PROVIDER_NAME,
          next=util.get_next_url(),
          _external=True,
        )
    )


def retrieve_user_from_odnoklassniki(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['uid'])
  user_db = models.User.get_by_id('auth_ids', auth_id)
  if user_db:
    return user_db

  return helpers.create_user_db(
      auth_id,
      response['name'],
      response['name'],
    )
