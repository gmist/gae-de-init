import flask

from core import task
from core import util
import config


def reset_password_notification(user_db):
  if not user_db.email:
    return
  user_db.token = util.uuid()
  user_db.put()

  to = '%s <%s>' % (user_db.name, user_db.email)
  body = '''Hello %(name)s,

it seems someone (hopefully you) tried to reset your password with %(brand)s.

In case it was you, please reset it by following this link:

%(link)s

If it wasn't you, we apologize. You can either ignore this email or reply to it
so we can take a look.

Best regards,
%(brand)s
''' % {
      'name': user_db.name,
      'link': flask.url_for('auth.user_reset', token=user_db.token, _external=True),
      'brand': config.CONFIG_DB.brand_name,
    }

  flask.flash(
      'A reset link has been sent to your email address.',
      category='success',
    )
  task.send_mail_notification('Reset your password', body, to)


def activate_user_notification(user_db):
  if not user_db.email:
    return
  user_db.token = util.uuid()
  user_db.put()

  to = user_db.email
  body = '''Welcome to %(brand)s.

Follow the link below to confirm your email address and activate your account:

%(link)s

If it wasn't you, we apologize. You can either ignore this email or reply to it
so we can take a look.

Best regards,
%(brand)s
''' % {
      'link': flask.url_for('auth.user_activate', token=user_db.token, _external=True),
      'brand': config.CONFIG_DB.brand_name,
    }

  flask.flash(
      'An activation link has been sent to your email address.',
      category='success',
    )
  task.send_mail_notification('Activate your account', body, to)

