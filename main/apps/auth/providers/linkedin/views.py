# coding: utf-8
from google.appengine.api import urlfetch
from flask.ext.oauthlib import client as oauth
import flask
import unidecode

from app import app
from apps.auth import helpers
from apps.auth.models import AuthProviders
from apps.user import models
from core import util
from .import CONFIG


PROVIDERS_DB = AuthProviders.get_master_db()
PROVIDER_NAME = CONFIG['name']
PROVIDER_KEY = 'OAUTH_%s' % PROVIDER_NAME


bp = helpers.make_provider_bp(PROVIDER_NAME, __name__)
provider_oauth = oauth.OAuth()

app.config[PROVIDER_KEY] = dict(
    base_url='https://api.linkedin.com/v1/',
    request_token_url=None,
    access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    access_token_params={'grant_type': 'authorization_code'},
    access_token_method='POST',
    authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
    consumer_key=PROVIDERS_DB.get_field('%s_api_key' % PROVIDER_NAME),
    consumer_secret=PROVIDERS_DB.get_field('%s_secret_key' % PROVIDER_NAME),
    request_token_params={
        'scope': 'r_basicprofile r_emailaddress',
        'state': util.uuid(),
      },
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
  flask.session['access_token'] = (resp['access_token'], '')
  fields = 'id,first-name,last-name,email-address'
  profile_url = '%speople/~:(%s)?oauth2_access_token=%s' % (
      provider.base_url, fields, resp['access_token'],
    )
  result = urlfetch.fetch(
      profile_url,
      headers={'x-li-format': 'json', 'Content-Type': 'application/json'}
    )
  try:
    content = flask.json.loads(result.content)
  except ValueError:
    return "Unknown error: invalid response from LinkedIn"
  if result.status_code != 200:
    return 'Unknown error: status=%s message=%s' % (
        content['status'], content['message'],
      )
  user_db = retrieve_user_from_linkedin(content)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_linkedin_oauth_token():
  return flask.session.get('access_token')


@bp.route('/signin/%s/' % PROVIDER_NAME)
def signin():
  flask.session['access_token'] = None
  helpers.save_request_params()
  return provider.authorize(callback=flask.url_for(
      'auth.p.%s.authorized' % PROVIDER_NAME, _external=True
    ))


def retrieve_user_from_linkedin(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  full_name = ' '.join([response['firstName'], response['lastName']]).strip()
  return helpers.create_user_db(
      auth_id,
      full_name,
      response['emailAddress'] or unidecode.unidecode(full_name),
      response['emailAddress'],
    )

