# coding: utf-8
from google.appengine.ext import ndb
from flask.ext import login

from apps.auth.models import AnonymousUser
from apps.auth.models import FlaskUser


login_manager = login.LoginManager()
login_manager.anonymous_user = AnonymousUser


def current_user_id():
  return login.current_user.id


def current_user_key():
  return login.current_user.user_db.key if login.current_user.user_db else None


def current_user_db():
  return login.current_user.user_db


def is_logged_in():
  return login.current_user.id != 0


@login_manager.user_loader
def load_user(key):
  user_db = ndb.Key(urlsafe=key).get()
  if user_db:
    return FlaskUser(user_db)
  return None
