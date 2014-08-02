# coding: utf-8
from flask.ext import login
import flask

from apps.auth import PROVIDERS_CONFIG
from apps.auth import models
from core import util


bp = flask.Blueprint(
    'auth',
    __name__,
    url_prefix='/auth',
    template_folder='templates',
  )


@bp.route('/login/')
@bp.route('/signin/')
def signin():
  next_url = util.get_next_url()
  if flask.url_for('auth.signin') in next_url:
    next_url = flask.url_for('pages.welcome')

  signin_urls = {}
  auth_db = models.AuthProviders.get_master_db()
  auth_providers = []
  for provider in PROVIDERS_CONFIG:
    name = provider.get('name')
    has_fields = True
    for field in provider.get('key_fields', {}).iterkeys():
      if not hasattr(auth_db, field) or not getattr(auth_db, field):
        has_fields = False

    if name and has_fields:
      auth_providers.append(provider)
      # signin_urls[name] = {
      #     'template_signin': provider.get('template_signin'),
      #     'signin_url': flask.url_for('auth.%s.signin' % name, next=next_url)
      #   }

  return flask.render_template(
      'auth/signin.html',
      title='Please sign in',
      html_class='signin',
      auth_providers=auth_providers,
      next_url=next_url,
    )


@bp.route('/signout/')
def signout():
  login.logout_user()
  flask.flash(u'You have been signed out.', category='success')
  return flask.redirect(flask.url_for('pages.welcome'))
