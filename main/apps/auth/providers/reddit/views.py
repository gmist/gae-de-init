# coding: utf-8
from base64 import b64encode
from flask.ext.oauthlib import client as oauth
import flask
import unidecode
from werkzeug import urls

from apps.auth import helpers
from apps.user import models
from .import CONFIG


PROVIDER_NAME = CONFIG['name']
bp = helpers.make_provider_bp(PROVIDER_NAME, __name__)
provider = helpers.make_provider(CONFIG)


def reddit_get_token():
  access_args = {
      'code': flask.request.args.get('code'),
      'client_id': provider.consumer_key,
      'client_secret': provider.consumer_secret,
      'redirect_uri': flask.session.get(provider.name + '_oauthredir'),
    }
  access_args.update(provider.access_token_params)
  auth = 'Basic ' + b64encode(
      ('%s:%s' % (provider.consumer_key, provider.consumer_secret)).encode(
          'latin1')).strip().decode('latin1')
  resp, content = provider._client.request(
      provider.expand_url(provider.access_token_url),
      provider.access_token_method,
      urls.url_encode(access_args),
      headers={'Authorization': auth},
    )

  data = oauth.parse_response(resp, content)
  if not provider.status_okay(resp):
    raise oauth.OAuthException(
        'Invalid response from ' + provider.name,
        type='invalid_response', data=data,
      )
  return data


provider.handle_oauth2_response = reddit_get_token


@bp.route('/authorized/')
@provider.authorized_handler
def authorized(resp):
  if flask.request.args.get('error'):
    return 'Access denied: error=%s' % (flask.request.args['error'])

  flask.session['oauth_token'] = (resp['access_token'], '')
  me = provider.request(
      'me',
      headers={'Authorization': 'Bearer %s' % resp['access_token']},
    )
  user_db = retrieve_user_from_reddit(me.data)
  return helpers.signin_user_db(user_db)


@provider.tokengetter
def get_reddit_oauth_token():
  return flask.session.get('oauth_token')


@bp.route('/signin/')
def signin():
  helpers.save_request_params()
  return provider.authorize(callback=flask.url_for(
      'auth.p.%s.authorized' % PROVIDER_NAME, _external=True
    ))


def retrieve_user_from_reddit(response):
  auth_id = '%s_%s' % (PROVIDER_NAME, response['id'])
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    return user_db
  return helpers.create_user_db(
      auth_id,
      response['name'],
      unidecode.unidecode(response['name']),
    )
