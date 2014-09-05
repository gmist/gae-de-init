# coding: utf-8
import re
from google.appengine.ext import ndb
from flask.ext import login
import flask
import unidecode

from apps.auth.models import FlaskUser
from apps.user import models
from core import task
from core import util
import config


def create_user_db(auth_id, name, username, email='', verified=False, **props):
  email = email.lower()
  if verified and email:
    user_dbs, _ = models.User.get_dbs(email=email, verified=True, limit=2)
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
  while not models.User.is_username_available(new_username):
    new_username = '%s%d' % (username, n)
    n += 1

  user_db = models.User(
      name=name,
      email=email,
      username=new_username,
      auth_ids=[auth_id],
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
