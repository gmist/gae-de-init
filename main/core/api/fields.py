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


class DateTime(fields.Raw):
  def format(self, value):
    return value.isoformat()


class Id(fields.Raw):
  def format(self, value):
    if value:
      return value.id()
    return None

def get_field_type(value):
  if is_blob(value):
    return Blob
  if is_blob_key(value):
    return BlobKey
  if is_geo_pt(value):
    return GeoPt
  # if is_key(value):
  #   return Key
  if is_date_time(value):
    return DateTime
  if is_float(value):
    return fields.Float
  if is_integer(value):
    return Integer
  if is_string(value):
    return fields.String
  return fields.String

def get_marshal_table(model_db):
  table = {}
  for prop in model_db._PROPERTIES:
    if prop == 'id':
      try:
        getattr(model_db, 'key')
        table['id'] = Id(attribute='key')
      except AttributeError:
        table['id'] = fields.Raw()
    else:
      table[prop] = get_field_type(getattr(model_db, prop, None))
  return table
