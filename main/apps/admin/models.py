# coding: utf-8
from google.appengine.ext import ndb
from flask.ext.restful import fields
import funcy

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
  check_unique_email = ndb.BooleanProperty(default=True)
  feedback_email = ndb.StringProperty(default='')
  flask_secret_key = ndb.StringProperty(default=util.uuid())
  notify_on_new_user = ndb.BooleanProperty(default=True)
  recaptcha_private_key = ndb.StringProperty(default='')
  recaptcha_public_key = ndb.StringProperty(default='')
  send_error_reports = ndb.BooleanProperty(default=False)
  verify_email = ndb.BooleanProperty(default=True)
  yandex_metrika_counter_number = ndb.StringProperty(default='')

  @classmethod
  def get_master_db(cls):
    return cls.get_or_insert('master')


config_fields = funcy.merge(base.base_fields, {
    'analytics_id': fields.String,
    'announcement_html': fields.String,
    'announcement_type': fields.String,
    'brand_name': fields.String,
    'check_unique_email': fields.Boolean,
    'feedback_email': fields.String,
    'flask_secret_key': fields.String,
    'notify_on_new_user': fields.Boolean,
    'recaptcha_private_key': fields.String,
    'recaptcha_public_key': fields.String,
    'send_error_reports': fields.Boolean,
    'verify_email': fields.Boolean,
    'yandex_metrika_counter_number': fields.String,
  })
