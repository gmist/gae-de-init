# coding: utf-8
import re
from google.appengine.api import users
import flask

from apps.auth import helpers
from apps.user import models
from core import util
from .import CONFIG


PROVIDER_NAME = CONFIG['name']

bp = helpers.make_provider_bp(PROVIDER_NAME, __name__)


@bp.route('/signin/')
def signin():
  helpers.save_request_params()
  google_url = users.create_login_url(
      flask.url_for('auth.p.%s.authorized' % PROVIDER_NAME)
    )
  return flask.redirect(google_url)


@bp.route('/authorized/')
def authorized():
  google_user = users.get_current_user()
  if google_user is None:
    flask.flash(u'You denied the request to sign in.')
    return flask.redirect(util.get_next_url())

  user_db = retrieve_user_from_google(google_user)
  return helpers.signin_user_db(user_db)


def retrieve_user_from_google(google_user):
  auth_id = '%s_%s' % (PROVIDER_NAME, google_user.user_id())
  user_db = models.User.get_by('auth_ids', auth_id)
  if user_db:
    if not user_db.admin and users.is_current_user_admin():
      user_db.admin = True
      user_db.put()
    return user_db

  return helpers.create_user_db(
      auth_id,
      re.sub(r'_+|-+|\.+', ' ', google_user.email().split('@')[0]).title(),
      google_user.email(),
      google_user.email(),
      verified=True,
      admin=users.is_current_user_admin(),
    )
