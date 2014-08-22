# coding: utf-8
import hashlib
from google.appengine.ext import ndb
from flask.ext.restful import fields
import funcy

from core import base
from core import util
import config


class User(base.Base):
  name = ndb.StringProperty(required=True)
  username = ndb.StringProperty(required=True)
  email = ndb.StringProperty(default='')
  auth_ids = ndb.StringProperty(repeated=True)
  active = ndb.BooleanProperty(default=True)
  admin = ndb.BooleanProperty(default=False)
  permissions = ndb.StringProperty(repeated=True)
  token = ndb.StringProperty(default='')
  verified = ndb.BooleanProperty(default=False)

  def has_permission(self, perm):
    return self.admin or perm in self.permissions

  def avatar_url_size(self, size=None):
    return '//gravatar.com/avatar/%(hash)s?d=identicon&r=x%(size)s' % {
        'hash': hashlib.md5(self.email or self.username).hexdigest(),
        'size': '&s=%d' % size if size > 0 else '',
      }
  avatar_url = property(avatar_url_size)

  @classmethod
  def get_dbs(cls, admin=None, active=None, verified=None, permissions=None, **kwargs):
    return super(User, cls).get_dbs(
        admin=admin or util.param('admin', bool),
        active=active or util.param('active', bool),
        verified=verified or util.param('verified', bool),
        permissions=permissions or util.param('permissions', list),
        **kwargs
      )

  @classmethod
  def is_username_available(cls, username, self_db=None):
    if self_db is None:
      return cls.get_by('username', username) is None
    user_dbs, _, _ = util.get_dbs(
        cls.query(), username=username, limit=2, keys_only=True
      )
    return not user_dbs or self_db in user_dbs and not user_dbs[1:]

  @classmethod
  def is_email_available(cls, email, self_db=None):
    if not config.CONFIG_DB.check_unique_email:
      return True
    user_dbs, _, _ = util.get_dbs(
        cls.query(), email=email, verified=True, limit=2, keys_only=True
      )
    return not user_dbs or self_db in user_dbs and not user_dbs[1:]


user_fields = funcy.merge(
    base.base_fields, {
        'active': fields.Boolean,
        'admin': fields.Boolean,
        'auth_ids': fields.List(fields.String),
        'avatar_url': fields.String,
        'email': fields.String,
        'name': fields.String,
        'username': fields.String,
        'permissions': fields.List(fields.String),
        'token': fields.String,
        'verified': fields.Boolean,
  })
