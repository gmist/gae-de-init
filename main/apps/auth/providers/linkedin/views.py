# coding: utf-8
import flask

from apps.auth import helpers
from apps.user import models
from .import CONFIG


provider = helpers.make_provider(CONFIG)
bp = helpers.make_provider_bp(provider.name, __name__)


def change_linkedin_query(uri, headers, body):
    auth = headers.pop('Authorization')
    headers['x-li-format'] = 'json'
    if auth:
        auth = auth.replace('Bearer', '').strip()
        if '?' in uri:
            uri += '&oauth2_access_token=' + auth
        else:
            uri += '?oauth2_access_token=' + auth
    return uri, headers, body

provider.pre_request = change_linkedin_query


@bp.route('/authorized/')
def authorized():
  response = provider.authorized_response()
  if response is None:
    return 'Access denied: error=%s error_description=%s' % (
        flask.request.args['error'],
        flask.request.args['error_description'],
      )
  flask.session['access_token'] = (response['access_token'], '')
  fields = 'id,first-name,last-name,email-address'
  profile_url = '%speople/~:(%s)' % (
      provider.base_url, fields,
    )
  result = provider.get(profile_url)
  if result.status != 200:
    return 'Unknown error: status=%s message=%s' % (
        result.data['status'], result.data['message'],
      )
  user_db = retrieve_user_from_linkedin(result.data)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_linkedin_oauth_token():
  return flask.session.get('access_token')


@bp.route('/signin/%s/' % provider.name)
def signin():
  return helpers.signin(provider)


def retrieve_user_from_linkedin(response):
  auth_id = '%s_%s' % (provider.name, response['id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  first_name = response.get('firstName', '')
  last_name = response.get('lastName', '')
  full_name = ' '.join([first_name, last_name]).strip()
  email = response.get('emailAddress', '')
  return helpers.create_user_db(
      auth_id=auth_id,
      name=full_name,
      username=email or full_name,
      email=email,
      verified=bool(email)
    )

