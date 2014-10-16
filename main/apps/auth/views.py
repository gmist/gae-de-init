# coding: utf-8
from flask.ext import login
import copy
import flask

from apps import auth
from apps.auth import forms
from apps.auth import helpers
from apps.auth import models
from apps.auth import tasks
from apps.user import models as u_models
from core import cache
from core import task
from core import util
import config

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
      for field in provider.get('fields', {}).iterkeys():
        try:
          getattr(auth_db, field)
        except AttributeError:
          setattr(auth_db, field, '')
    form.populate_obj(auth_db)
    auth_db.put()
    return flask.redirect(flask.url_for('admin.index'))
  for provider in auth_providers:
    provider_keys = sorted(provider.get('fields', {}).keys())
    form_key_fields = [getattr(form, field) for field in provider_keys]
    provider['fields'] = form_key_fields
  return flask.render_template(
      'auth/admin/index.html',
      title='Auth Config',
      form=form,
      auth_providers=auth_providers,
      api_url=flask.url_for('api.auth.providers'),
    )


@bp.route('/signin/', methods=['GET', 'POST'], endpoint='signin')
def signin():
  next_url = util.get_next_url()
  form = None
  if config.CONFIG_DB.has_email_authentication:
    form = helpers.form_with_recaptcha(forms.SignInForm())
    helpers.save_request_params()
    if form.validate_on_submit():
      result = helpers.retrieve_user_from_email(
          form.email.data, form.password.data)
      if result:
        cache.reset_auth_attempt()
        return helpers.signin_user_db(result)
      if result is None:
        form.email.errors.append('Email or Password do not match')
      if result is False:
        return flask.redirect(flask.url_for('welcome'))
    if not form.errors:
      form.next_url.data = next_url

  if form and form.errors:
    cache.bump_auth_attempt()

  return flask.render_template(
      'auth/auth.html',
      title='Sign in',
      html_class='auth',
      auth_providers=get_auth_providers(next_url),
      next_url=next_url,
      form=form,
      form_type='signin' if config.CONFIG_DB.has_email_authentication else '',
    )


@bp.route('/signup/', methods=['GET', 'POST'], endpoint='signup')
def singup():
  next_url = util.get_next_url()
  form = None
  if config.CONFIG_DB.has_email_authentication:
    form = helpers.form_with_recaptcha(forms.SignUpForm())
    helpers.save_request_params()
    if form.validate_on_submit():
      user_db = u_models.User.get_by('email', form.email.data)
      if user_db:
        form.email.errors.append(u'This email is already taken.')

      if not form.errors:
        user_db = helpers.create_user_db(
            None,
            util.create_name_from_email(form.email.data),
            form.email.data,
            form.email.data,
          )
        user_db.put()
        tasks.activate_user_notification(user_db)
        cache.bump_auth_attempt()
        return flask.redirect(flask.url_for('pages.welcome'))

  if form and form.errors:
    cache.bump_auth_attempt()

  title = 'Sign up' if config.CONFIG_DB.has_email_authentication else 'Sign in'
  return flask.render_template(
      'auth/auth.html',
      title=title,
      html_class='auth',
      next_url=next_url,
      form=form,
      auth_providers=get_auth_providers(next_url),
    )


@bp.route('/signout/')
def signout():
  login.logout_user()
  flask.flash(u'You have been signed out.', category='success')
  return flask.redirect(flask.url_for('pages.welcome'))


@bp.route('/user/forgot/', methods=['GET', 'POST'])
def user_forgot(token=None):
  if not config.CONFIG_DB.has_email_authentication:
    flask.abort(418)

  form = helpers.form_with_recaptcha(
      forms.UserForgotForm(obj=auth.current_user_db()))
  if form.validate_on_submit():
    cache.bump_auth_attempt()
    email = form.email.data
    user_dbs, _, _ = util.get_dbs(
        u_models.User.query(), email=email, active=True, limit=2,
      )
    count = len(user_dbs)
    if count == 1:
      tasks.reset_password_notification(user_dbs[0])
      return flask.redirect(flask.url_for('pages.welcome'))
    elif count == 0:
      form.email.errors.append('This email was not found')
    elif count == 2:
      task.email_conflict_notification(email)
      form.email.errors.append(
          '''We are sorry but it looks like there is a conflict with your
          account. Our support team is already informed and we will get back to
          you as soon as possible.'''
        )

  if form.errors:
    cache.bump_auth_attempt()

  return flask.render_template(
      'auth/user_forgot.html',
      title='Forgot Password?',
      html_class='user-forgot',
      form=form,
    )

@bp.route('/user/reset/<token>/', methods=['GET', 'POST'])
@bp.route('/user/reset/', methods=['GET', 'POST'])
def user_reset(token=None):
  if token is None:
    flask.abort(404)

  user_db = u_models.User.get_by('token', token)
  if not user_db:
    flask.flash('That link is either invalid or expired.', category='danger')
    return flask.redirect(flask.url_for('welcome'))

  if auth.is_logged_in():
    login.logout_user()
    return flask.redirect(flask.request.path)

  form = forms.UserResetForm()
  if form.validate_on_submit():
    user_db.password_hash = helpers.password_hash(user_db, form.new_password.data)
    user_db.token = util.uuid()
    user_db.verified = True
    user_db.put()
    flask.flash('Your password was changed succesfully.', category='success')
    return helpers.signin_user_db(user_db)

  return flask.render_template(
      'auth/user_reset.html',
      title='Reset Password',
      html_class='user-reset',
      form=form,
      user_db=user_db,
    )


@bp.route('/user/activate/<token>/', methods=['GET', 'POST'])
def user_activate(token):
  if auth.is_logged_in():
    login.logout_user()
    return flask.redirect(flask.request.path)

  user_db = u_models.User.get_by('token', token)
  if not user_db:
    flask.flash('That link is either invalid or expired.', category='danger')
    return flask.redirect(flask.url_for('pages.welcome'))

  form = forms.UserActivateForm(obj=user_db)
  if form.validate_on_submit():
    form.populate_obj(user_db)
    user_db.password_hash = helpers.password_hash(user_db, form.password.data)
    user_db.token = util.uuid()
    user_db.verified = True
    user_db.put()
    return helpers.signin_user_db(user_db)

  return flask.render_template(
      'auth/user_activate.html',
      title='Activate Account',
      html_class='user-activate',
      user_db=user_db,
      form=form,
    )


def get_auth_providers(next_url):
  auth_db = models.AuthProviders.get_master_db()
  auth_providers = []
  for name, provider in auth.PROVIDERS_CONFIG.iteritems():
    for field in provider.get('fields', {}).iterkeys():
      if not hasattr(auth_db, field) or not getattr(auth_db, field):
        break
    else:
      provider['signin_url'] = flask.url_for(
        'auth.p.%s.signin' % name, next=next_url)
      auth_providers.append(provider)
  return sorted(auth_providers, key=lambda x: x.get('name'))
