# coding: utf-8
from google.appengine.api import urlfetch
import flask
import unidecode

from apps.auth import helpers
from apps.user import models
from .import CONFIG


PROVIDER_NAME = CONFIG['name']
bp = helpers.make_provider_bp(PROVIDER_NAME, __name__)
provider = helpers.make_provider(CONFIG)


@bp.route('/authorized/')
def authorized():
  resp = provider.authorized_response()
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

