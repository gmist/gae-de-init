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


class SignInForm(wtf.Form):
  email = wtforms.StringField(
      'Email',
      [wtforms.validators.required()],
      filters=[util.email_filter],
    )
  password = wtforms.StringField(
      'Password',
      [wtforms.validators.required()],
    )
  remember = wtforms.BooleanField(
      'Keep me signed in',
      [wtforms.validators.optional()],
    )
  recaptcha = wtf.RecaptchaField('Are you human?')
  next_url = wtforms.HiddenField()


class SignUpForm(wtf.Form):
  email = wtforms.StringField(
      'Email',
      [wtforms.validators.required(), wtforms.validators.email()],
      filters=[util.email_filter],
    )
  recaptcha = wtf.RecaptchaField('Are you human?')


class UserActivateForm(wtf.Form):
  name = wtforms.StringField(
      'Name',
      [wtforms.validators.required()], filters=[util.strip_filter],
    )
  password = wtforms.StringField(
      'Password',
      [wtforms.validators.required(), wtforms.validators.length(min=6)],
    )


class UserForgotForm(wtf.Form):
  email = wtforms.StringField(
      'Email',
      [wtforms.validators.required(), wtforms.validators.email()],
      filters=[util.email_filter],
    )
  recaptcha = wtf.RecaptchaField('Are you human?')


class UserResetForm(wtf.Form):
  new_password = wtforms.StringField(
      'New Password',
      [wtforms.validators.required(), wtforms.validators.length(min=6)],
    )

