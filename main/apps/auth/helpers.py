# coding: utf-8
import re
import hashlib

from google.appengine.ext import ndb
from flask.ext import login
from flask.ext.oauthlib import client as oauth
import flask
import unidecode

from app import app
from apps.auth.models import FlaskUser, AuthProviders
from apps.user import models as u_models
from core import task
from core import util
import config


PROVIDERS_DB = AuthProviders.get_master_db()


def create_user_db(auth_id, name, username, email='', verified=False, **props):
  email = email.lower() if email else ''
  if verified and email:
    user_dbs, _, _ = u_models.User.get_dbs(email=email, verified=True, limit=2)
    if len(user_dbs) == 1:
      user_db = user_dbs[0]
      user_db.auth_ids.append(auth_id)
      user_db.put()
      task.new_user_notification(user_db)
      return user_db

  if isinstance(username, str):
    username = username.decode('utf-8')
  username = unidecode.unidecode(username.split('@')[0].lower()).strip()
  username = re.sub(r'[\W_]+', '.', username)
  new_username = username
  n = 1
  while not u_models.User.is_username_available(new_username):
    new_username = '%s%d' % (username, n)
    n += 1

  user_db = u_models.User(
      name=name,
      email=email,
      username=new_username,
      auth_ids=[auth_id] if auth_id else [],
      **props
    )
  user_db.put()
  task.new_user_notification(user_db)
  return user_db


def save_request_params():
  flask.session['auth-params'] = {
      'next': util.get_next_url(),
      'remember': util.param('remember', bool),
    }


@ndb.toplevel
def signin_user_db(user_db):
  if not user_db:
    return flask.redirect(flask.url_for('auth.signin'))
  flask_user_db = FlaskUser(user_db)
  auth_params = flask.session.get('auth-params', {
      'next': flask.url_for('pages.welcome'),
      'remember': False,
    })
  if login.login_user(flask_user_db, remember=auth_params['remember']):
    user_db.put_async()
    flask.flash('Hello %s, welcome to %s.' % (
        user_db.name, config.CONFIG_DB.brand_name,
      ), category='success')
    return flask.redirect(util.get_next_url(auth_params['next']))
  flask.flash('Sorry, but you could not sign in.', category='danger')
  return flask.redirect(flask.url_for('auth.signin'))


def make_provider_bp(provider_name, module_name):
  return flask.Blueprint(
      'auth.p.%s' % provider_name,
      module_name,
      url_prefix='/auth/p/%s' % provider_name,
      template_folder='templates',
    )


def make_provider(provider_config):
  name = provider_config['name']
  key = 'oauth_%s' % name
  oauth_config = provider_config['oauth']
  provider_oauth = oauth.OAuth()
  app.config[key] = oauth_config
  provider = provider_oauth.remote_app(name, app_key=key)
  provider_oauth.init_app(app)
  return provider


def provider_field_name(provider_name, field_name):
  return '%s_%s' % (provider_name, field_name)


def get_consumer_key_field_name(provider_name):
  return provider_field_name(provider_name, 'consumer_key')


def get_consumer_secret_field_name(provider_name):
  return provider_field_name(provider_name, 'consumer_secret')


def get_consumer_key(provider_name):
  return PROVIDERS_DB.get_field(get_consumer_key_field_name(provider_name))


def get_consumer_secret(provider_name):
  return PROVIDERS_DB.get_field(get_consumer_secret_field_name(provider_name))


def make_provider_config(
        name, fields=None, oauth_config=None, title=None, icon_class=None):
  title = title or name.title()
  icon_class = icon_class or 'fa-%s' % name
  fields = fields or {}
  if oauth_config:
    oauth_config.update({
        'consumer_key': get_consumer_key(name),
        'consumer_secret': get_consumer_secret(name),
      })
  else:
    oauth_config = {}
  return {
      'name': name,
      'title': title,
      'icon_class': icon_class,
      'fields': fields,
      'oauth': oauth_config,
    }


def signin(provider, scheme='http'):
  flask.session.pop('oauth_token', None)
  save_request_params()
  return provider.authorize(flask.url_for(
      'auth.p.%s.authorized' % provider.name, _external=True, _scheme=scheme
    ))


def retrieve_user_from_email(email, password):
  user_dbs, _, _ = u_models.User.get_dbs(
      email=email, active=True, limit=2
    )
  if not user_dbs:
    return None
  if len(user_dbs) > 1:
    flask.flash('''We are sorry but it looks like there is a conflict with
        your account. Our support team is already informed and we will get
        back to you as soon as possible.''', category='danger')
    task.email_conflict_notification(email)
    return False

  user_db = user_dbs[0]
  if user_db.password_hash == password_hash(user_db, password):
    return user_db
  return None


def password_hash(user_db, password):
  m = hashlib.sha256()
  m.update(user_db.key.urlsafe())
  m.update(user_db.created.isoformat())
  m.update(m.hexdigest())
  m.update(password.encode('utf-8'))
  m.update(config.CONFIG_DB.salt)
  return m.hexdigest()
