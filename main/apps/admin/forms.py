# coding: utf-8
from flask.ext import wtf
import wtforms

from core import util
import models


class ConfigUpdateForm(wtf.Form):
  analytics_id = wtforms.StringField(
      'Tracking ID', filters=[util.strip_filter]
    )
  announcement_html = wtforms.TextAreaField(
      'Announcement HTML', filters=[util.strip_filter]
    )
  announcement_type = wtforms.SelectField(
      'Announcement Type',
      choices=[(t, t.title()) for t in models.Config.announcement_type._choices]
    )
  anonymous_recaptcha = wtforms.BooleanField(
      'Use reCAPTCHA in forms for unauthorized users'
    )
  brand_name = wtforms.StringField(
      'Brand Name',
      [wtforms.validators.required()],
      filters=[util.strip_filter]
    )
  check_unique_email = wtforms.BooleanField(
      'Check for the uniqueness of the verified emails'
    )
  email_authentication = wtforms.BooleanField(
      'Email authentication for sign in/sign up'
    )
  feedback_email = wtforms.StringField(
      'Feedback Email',
      [wtforms.validators.optional(), wtforms.validators.email()],
      filters=[util.email_filter]
    )
  flask_secret_key = wtforms.StringField(
      'Flask Secret Key',
      [wtforms.validators.optional()],
      filters=[util.strip_filter]
    )
  notify_on_new_user = wtforms.BooleanField(
      'Send an email notification when a user signs up'
    )
  recaptcha_private_key = wtforms.StringField(
      'Private Key', filters=[util.strip_filter]
    )
  recaptcha_public_key = wtforms.StringField(
      'Public Key', filters=[util.strip_filter]
    )
  salt = wtforms.StringField(
      'Salt', [wtforms.validators.optional()], filters=[util.strip_filter]
    )
  send_error_reports = wtforms.BooleanField('Send daily error reports')
  verify_email = wtforms.BooleanField('Verify user emails')
  yandex_metrika_counter_number = wtforms.StringField(
      'Counter number', filters=[util.strip_filter]
    )
