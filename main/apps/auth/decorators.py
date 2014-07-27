# coding: utf-8

import functools
from apps.auth.login_manager import current_user_db, is_logged_in
import flask

from app import app

_signals = flask.signals.Namespace()
permission_registered = _signals.signal('permission-registered')


def decorator_order_guard(f, decorator_name):
  if f in app.view_functions.values():
    raise SyntaxError(
        'Do not use %s above app.route decorators as it would not be checked. '
        'Instead move the line below the app.route lines.' % decorator_name
      )


def login_required(f):
  decorator_order_guard(f, 'auth.login_required')

  @functools.wraps(f)
  def decorated_function(*args, **kws):
    if is_logged_in():
      return f(*args, **kws)
    if flask.request.path.startswith('/_s/'):
      return flask.abort(401)
    return flask.redirect(flask.url_for('signin', next=flask.request.url))
  return decorated_function


def admin_required(f):
  decorator_order_guard(f, 'auth.admin_required')

  @functools.wraps(f)
  def decorated_function(*args, **kws):
    if is_logged_in() and current_user_db().admin:
      return f(*args, **kws)
    if not is_logged_in() and flask.request.path.startswith('/_s/'):
      return flask.abort(401)
    if not is_logged_in():
      return flask.redirect(flask.url_for('signin', next=flask.request.url))
    return flask.abort(403)
  return decorated_function


def permission_required(permission=None, methods=None):
  def permission_decorator(f):
    decorator_order_guard(f, 'auth.permission_required')

    # default to decorated function name as permission
    perm = permission or f.func_name
    meths = [m.upper() for m in methods] if methods else None

    permission_registered.send(f, permission=perm)

    @functools.wraps(f)
    def decorated_function(*args, **kws):
      if meths and flask.request.method.upper() not in meths:
        return f(*args, **kws)
      if is_logged_in() and current_user_db().has_permission(perm):
        return f(*args, **kws)
      if not is_logged_in():
        if flask.request.path.startswith('/_s/'):
          return flask.abort(401)
        return flask.redirect(flask.url_for('signin', next=flask.request.url))
      return flask.abort(403)
    return decorated_function
  return permission_decorator
