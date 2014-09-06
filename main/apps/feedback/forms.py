# coding: utf-8
from flask.ext import wtf
import wtforms

from core import util


class FeedbackForm(wtf.Form):
  name = wtforms.StringField(
      'Name',
      [wtforms.validators.required()],
      filters=[util.strip_filter]
    )
  message = wtforms.TextAreaField(
      'Message',
      [wtforms.validators.required()],
      filters=[util.strip_filter],
    )
  email = wtforms.StringField(
      'Your email (optional)',
      [wtforms.validators.optional(), wtforms.validators.email()],
      filters=[util.email_filter],
    )
  recaptcha = wtf.RecaptchaField('Are you human?')
  comment = wtforms.TextAreaField(
      'Comment',
      [wtforms.validators.optional()],
      filters=[util.strip_filter]
    )
