# coding: utf-8
import hashlib
from google.appengine.ext import ndb
from flask.ext.restful import fields
import funcy

from core import base, util


class User(base.Base):
  name = ndb.StringProperty(required=True)
  username = ndb.StringProperty(required=True)
  email = ndb.StringProperty(default='')
  auth_ids = ndb.StringProperty(repeated=True)
  active = ndb.BooleanProperty(default=True)
  admin = ndb.BooleanProperty(default=False)
  permissions = ndb.StringProperty(repeated=True)

  def has_permission(self, perm):
    return self.admin or perm in self.permissions

  def avatar_url_size(self, size=None):
    return '//gravatar.com/avatar/%(hash)s?d=identicon&r=x%(size)s' % {
        'hash': hashlib.md5(self.email or self.username).hexdigest(),
        'size': '&s=%d' % size if size > 0 else '',
      }
  avatar_url = property(avatar_url_size)

  _PROPERTIES = base.Base._PROPERTIES.union({
      'active',
      'admin',
      'auth_ids',
      'avatar_url',
      'email',
      'name',
      'username',
      'permissions',
    })

  @classmethod
  def get_dbs(cls, admin=None, active=None, permissions=None, **kwargs):
    return super(User, cls).get_dbs(
        admin=admin or util.param('admin', bool),
        active=active or util.param('active', bool),
        permissions=permissions or util.param('permissions', list),
        **kwargs
      )

  @classmethod
  def is_username_available(cls, username, self_db=None):
    if self_db is None:
      return cls.get_by('username', username) is None
    user_dbs, _ = util.get_dbs(cls.query(), username=username, limit=2)
    c = len(user_dbs)
    return not (c == 2 or c == 1 and self_db.key != user_dbs[0].key)


user_fields = funcy.merge(
    base.base_fields,
    {
        'active': fields.Boolean,
        'admin': fields.Boolean,
        'auth_ids': fields.List(fields.String),
        'avatar_url': fields.String,
        'email': fields.String,
        'name': fields.String,
        'username': fields.String,
        'permissions': fields.List(fields.String)
  })
