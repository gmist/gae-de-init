# coding: utf-8
from flask.ext import wtf
import wtforms

from core import util


class AuthProvidersForm(wtf.Form):
  @classmethod
  def append_providers(cls, providers):
    for provider in providers:
      for field, label in provider.get('fields', {}).iteritems():
        setattr(
            cls,
            '%s' % field,
            wtforms.StringField(label, filters=[util.strip_filter])
          )
    return cls
