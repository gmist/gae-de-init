# coding: utf-8
import urllib
from google.appengine.ext import ndb

import funcy
from flask.ext.restful import fields


is_boolean = funcy.isa(ndb.BooleanProperty)
is_blob = funcy.isa(ndb.BlobProperty)
is_blob_key = funcy.isa(ndb.BlobKey)
is_float = funcy.isa(ndb.FloatProperty)
is_date_time = funcy.isa(ndb.DateTimeProperty, ndb.DateProperty)
is_geo_pt = funcy.isa(ndb.GeoPt)
is_integer = funcy.isa(ndb.IntegerProperty)
is_key = funcy.isa(ndb.Key)
is_string = funcy.isa(ndb.StringProperty, ndb.TextProperty)


class GeoPt(fields.Raw):
  def format(self, value):
    return '%s,%s' % (value.lat, value.lon)


class Key(fields.Raw):
  def format(self, value):
    return value.urlsafe()


class BlobKey(fields.Raw):
  def format(self, value):
    return urllib.quote(str(value))


class Blob(fields.Raw):
  def format(self, value):
    return repr(value)


class Integer(fields.Raw):
  def format(self, value):
    if value > 9007199254740992 or value < -9007199254740992:
      return repr(value)
    return value


class DateTime(fields.Raw):
  def format(self, value):
    return value.isoformat()


class Id(fields.Raw):
  def output(self, key, obj):
    try:
      value = getattr(obj, 'key', None).id()
      return super(Id, self).output(key, {'id': value})
    except AttributeError:
      return None
