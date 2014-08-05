# coding: utf-8
from google.appengine.ext import ndb

from core import base
from core import util


class Feedback(base.Base):
  subject = ndb.StringProperty()
  message = ndb.TextProperty()
  email = ndb.StringProperty()
  comment = ndb.TextProperty()
  is_read = ndb.BooleanProperty(default=False)
  user = ndb.KeyProperty()

  @classmethod
  def get_dbs(cls, is_read=None, **kwargs):
    return super(Feedback, cls).get_dbs(
        is_read=is_read or util.param('is_read', bool),
        **kwargs
      )
