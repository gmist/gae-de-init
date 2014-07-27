# coding: utf-8
from google.appengine.ext import ndb
from flask.ext import login


class AnonymousUser(login.AnonymousUserMixin):
  id = 0
  admin = False
  name = 'Anonymous'
  user_db = None

  def key(self):
    return None

  def has_permission(self, permission):
    return False


class FlaskUser(AnonymousUser):
  def __init__(self, user_db):
    self.user_db = user_db
    self.id = user_db.key.id()
    self.name = user_db.name
    self.admin = user_db.admin

  def key(self):
    return self.user_db.key.urlsafe()

  def get_id(self):
    return self.user_db.key.urlsafe()

  def is_authenticated(self):
    return True

  def is_active(self):
    return self.user_db.active

  def is_anonymous(self):
    return False

  def has_permission(self, permission):
    return self.user_db.has_permission(permission)


class AuthProviders(ndb.Expando):
  def get_field(self, field_name):
    try:
      return getattr(AuthProviders.get_master_db(), field_name)
    except AttributeError:
      return ''

  @classmethod
  def get_master_db(cls):
    return cls.get_or_insert('master')

  def has_provider(self, *fields):
    for filed in fields:
      if not self.get_field(filed):
        return False
    return True
