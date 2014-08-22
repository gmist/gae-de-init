# coding: utf-8
from flask.ext import wtf
from core import util


class FeedbackForm(wtf.Form):
  name = wtf.StringField(
      'Name',
      [wtf.validators.required()],
      filters=[util.strip_filter]
    )
  subject = wtf.StringField(
      'Subject',
      [wtf.validators.required()],
      filters=[util.strip_filter],
    )
  message = wtf.TextAreaField(
      'Message',
      [wtf.validators.required()],
      filters=[util.strip_filter],
    )
  email = wtf.StringField(
      'Your email (optional)',
      [wtf.validators.optional(), wtf.validators.email()],
      filters=[util.email_filter],
    )
  comment = wtf.TextAreaField(
      'Comment',
      [wtf.validators.optional()],
      filters=[util.strip_filter]
    )
