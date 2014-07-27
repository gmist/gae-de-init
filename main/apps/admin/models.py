# coding: utf-8
from google.appengine.ext import ndb

from core import base
from core import util
import config


class Config(base.Base):
  analytics_id = ndb.StringProperty(default='')
  announcement_html = ndb.TextProperty(default='')
  announcement_type = ndb.StringProperty(default='info', choices=[
      'info', 'warning', 'success', 'danger',
    ])
  brand_name = ndb.StringProperty(default=config.APPLICATION_ID)
  feedback_email = ndb.StringProperty(default='')
  flask_secret_key = ndb.StringProperty(default=util.uuid())
  notify_on_new_user = ndb.BooleanProperty(default=True)

  _PROPERTIES = base.Base._PROPERTIES.union({
      'analytics_id',
      'announcement_html',
      'announcement_type',
      'brand_name',
      'feedback_email',
      'flask_secret_key',
      'notify_on_new_user',
    })

  @classmethod
  def get_master_db(cls):
    return cls.get_or_insert('master')
