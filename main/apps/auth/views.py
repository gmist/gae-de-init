# coding: utf-8
import copy
from flask.ext import login
import flask

from apps import auth
from apps.auth import PROVIDERS_CONFIG
from apps.auth import forms
from apps.auth import models
from core import util


bpa = flask.Blueprint(
    'auth.admin',
    __name__,
    url_prefix='/admin/auth',
    template_folder='templates'
  )

bp = flask.Blueprint(
    'auth',
    __name__,
    url_prefix='/auth',
    template_folder='templates',
  )

@bpa.route('/', methods=['GET', 'POST'], endpoint='index')
@auth.admin_required
def admin_index():
  auth_db = models.AuthProviders.get_master_db()
  auth_providers = copy.deepcopy(auth.PROVIDERS_CONFIG.values())
  auth_providers = sorted(auth_providers, key=lambda x: x.get('name'))
  form = forms.AuthProvidersForm.append_providers(
      auth_providers)(obj=auth_db)
  if form.validate_on_submit():
    for provider in auth_providers:
      for field in provider.get('key_fields', {}).iterkeys():
        try:
          getattr(auth_db, field)
        except AttributeError:
          setattr(auth_db, field, '')
    form.populate_obj(auth_db)
    auth_db.put()
    return flask.redirect(flask.url_for('admin.index'))
  for provider in auth_providers:
    provider_keys = sorted(provider.get('key_fields', {}).keys())
    form_key_fields = [getattr(form, field) for field in provider_keys]
    provider['key_fields'] = form_key_fields
  return flask.render_template(
      'auth/admin/index.html',
      title='Auth Config',
      form=form,
      auth_providers=auth_providers,
      api_url=flask.url_for('api.auth.providers'),
    )

@bp.route('/login/')
@bp.route('/signin/')
def signin():
  next_url = util.get_next_url()
  if flask.url_for('auth.signin') in next_url:
    next_url = flask.url_for('pages.welcome')

  auth_db = models.AuthProviders.get_master_db()
  auth_providers = []
  for name, provider in PROVIDERS_CONFIG.iteritems():
    for field in provider.get('key_fields', {}).iterkeys():
      if not hasattr(auth_db, field) or not getattr(auth_db, field):
        break
    else:
      provider['signin_url'] = flask.url_for('auth.p.%s.signin' % name, next=next_url)
      auth_providers.append(provider)

  return flask.render_template(
      'auth/signin.html',
      title='Please sign in',
      html_class='signin',
      auth_providers=sorted(auth_providers, key=lambda x: x.get('name')),
      next_url=next_url,
    )


@bp.route('/signout/')
def signout():
  login.logout_user()
  flask.flash(u'You have been signed out.', category='success')
  return flask.redirect(flask.url_for('pages.welcome'))
