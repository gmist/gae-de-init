# coding: utf-8
import copy
from google.appengine.ext import ndb
import flask

from apps import auth
from apps.auth import helpers
from core import task
from core import util
import config
import forms
import models


bp = flask.Blueprint(
    'user',
    __name__,
    url_prefix='/user',
    template_folder='templates',
  )


###############################################################################
# User List
###############################################################################
@bp.route('/', endpoint='list')
@auth.admin_required
def user_list():
  user_dbs, user_cursor, prev_cursor = models.User.get_dbs(
      email=util.param('email')
    )
  permissions = list(forms.UserUpdateForm._permission_choices)
  permissions += util.param('permissions', list) or []
  return flask.render_template(
      'user/admin/list.html',
      html_class='user-list',
      title='User List',
      user_dbs=user_dbs,
      next_url=util.generate_next_url(user_cursor),
      prev_url=util.generate_next_url(prev_cursor),
      permissions=sorted(set(permissions)),
      api_url=flask.url_for('api.users')
    )


@bp.route('/<int:user_id>/update/', methods=['GET', 'POST'], endpoint='update')
@auth.admin_required
def user_update(user_id):
  user_db = models.User.get_by_id(user_id)
  if not user_db:
    flask.abort(404)

  form = forms.UserUpdateForm(obj=user_db)
  for permission in user_db.permissions:
    form.permissions.choices.append((permission, permission))
  form.permissions.choices = sorted(set(form.permissions.choices))
  if form.validate_on_submit():
    if not util.is_valid_username(form.username.data):
      form.username.errors.append('This username is invalid.')
    elif not models.User.is_username_available(form.username.data, user_db.key):
      form.username.errors.append('This username is already taken.')
    else:
      form.populate_obj(user_db)
      if auth.current_user_id() == user_db.key.id():
        user_db.admin = True
        user_db.active = True
      user_db.put()
      return flask.redirect(flask.url_for(
          'user.list', order='-modified', active=user_db.active,
        ))

  return flask.render_template(
      'user/admin/update.html',
      title=user_db.name,
      html_class='user-update',
      form=form,
      user_db=user_db,
      api_url=flask.url_for('api.user', key=user_db.key.urlsafe())
    )


@bp.route('/verify_email/<token>/')
@auth.login_required
def verify_email(token):
  user_db = auth.current_user_db()
  if user_db.token != token:
    flask.flash('That link is either invalid or expired.', category='danger')
    return flask.redirect(flask.url_for('user.profile_update'))
  user_db.verified = True
  user_db.token = util.uuid()
  user_db.put()
  flask.flash('Hooray! Your email is now verified.', category='success')
  return flask.redirect(flask.url_for('user.profile_update'))


@bp.route('/merge/', methods=['GET', 'POST'])
@auth.admin_required
def merge():
  user_keys = util.param('user_keys', list)
  if not user_keys:
    flask.abort(400)

  user_db_keys = [ndb.Key(urlsafe=k) for k in user_keys]
  user_dbs = ndb.get_multi(user_db_keys)
  if len(user_dbs) < 2:
    flask.abort(400)

  user_dbs.sort(key=lambda user_db: user_db.created)
  merged_user_db = user_dbs[0]
  auth_ids = []
  permissions = []
  is_admin = False
  is_active = False
  for user_db in user_dbs:
    auth_ids.extend(user_db.auth_ids)
    permissions.extend(user_db.permissions)
    is_admin = is_admin or user_db.admin
    is_active = is_active or user_db.active
    if user_db.key.urlsafe() == util.param('user_key'):
      merged_user_db = user_db

  auth_ids = sorted(list(set(auth_ids)))
  permissions = sorted(list(set(permissions)))
  merged_user_db.permissions = permissions
  merged_user_db.admin = is_admin
  merged_user_db.active = is_active
  merged_user_db.verified = False

  form_obj = copy.deepcopy(merged_user_db)
  form_obj.user_key = merged_user_db.key.urlsafe()
  form_obj.user_keys = ','.join(user_keys)

  form = forms.UserMergeForm(obj=form_obj)
  if form.validate_on_submit():
    form.populate_obj(merged_user_db)
    merged_user_db.auth_ids = auth_ids
    merged_user_db.put()

    deprecated_keys = [k for k in user_db_keys if k != merged_user_db.key]
    merge_user_dbs(merged_user_db, deprecated_keys)
    return flask.redirect(
        flask.url_for('user.update', user_id=merged_user_db.key.id()),
      )

  return flask.render_template(
      'user/admin/merge.html',
      title='Merge Users',
      html_class='user-merge',
      user_dbs=user_dbs,
      merged_user_db=merged_user_db,
      form=form,
      auth_ids=auth_ids,
      api_url=flask.url_for('api.users', user_keys=','.join(user_keys))
    )


@ndb.transactional(xg=True)
def merge_user_dbs(user_db, deprecated_keys):
  # TODO: Merge possible user data before handling deprecated users
  deprecated_dbs = ndb.get_multi(deprecated_keys)
  for deprecated_db in deprecated_dbs:
    deprecated_db.auth_ids = []
    deprecated_db.active = False
    deprecated_db.verified = False
    if not deprecated_db.username.startswith('_'):
      deprecated_db.username = '_%s' % deprecated_db.username
  ndb.put_multi(deprecated_dbs)


@bp.route('/profile/')
@auth.login_required
def profile():
  user_db = auth.current_user_db()
  return flask.render_template(
      'user/profile/index.html',
      title=user_db.name,
      html_class='profile-view',
      user_db=user_db,
      has_json=True,
      api_url=flask.url_for('api.user', key=user_db.key.urlsafe()),
    )


@bp.route('/profile/update/', methods=['GET', 'POST'])
@auth.login_required
def profile_update():
  user_db = auth.current_user_db()
  form = forms.ProfileUpdateForm(obj=user_db)

  if form.validate_on_submit():
    email = form.email.data
    if email and not user_db.is_email_available(email, user_db.key):
      form.email.errors.append('This email is already taken.')

    if not form.errors:
      send_verification = not user_db.token or user_db.email != email
      form.populate_obj(user_db)
      if send_verification:
        user_db.verified = False
        task.verify_email_notification(user_db)
      user_db.put()
      return flask.redirect(flask.url_for('pages.welcome'))

  return flask.render_template(
      'user/profile/update.html',
      title=user_db.name,
      html_class='profile',
      form=form,
      user_db=user_db,
    )


@bp.route('/profile/password/', methods=['GET', 'POST'])
@auth.login_required
def profile_password():
  if not config.CONFIG_DB.has_email_authentication:
    flask.abort(418)
  user_db = auth.current_user_db()
  form = forms.ProfilePasswordForm(obj=user_db)

  if form.validate_on_submit():
    errors = False
    old_password = form.old_password.data
    new_password = form.new_password.data
    if new_password or old_password:
      if user_db.password_hash:
        if helpers.password_hash(user_db, old_password) != user_db.password_hash:
          form.old_password.errors.append('Invalid current password')
          errors = True
      if not errors and old_password and not new_password:
        form.new_password.errors.append('This field is required.')
        errors = True

      if not (form.errors or errors):
        user_db.password_hash = helpers.password_hash(user_db, new_password)
        flask.flash('Your password has been changed.', category='success')

    if not (form.errors or errors):
      user_db.put()
      return flask.redirect(flask.url_for('user.profile'))

  return flask.render_template(
      'user/profile/password.html',
      title=user_db.name,
      html_class='profile-password',
      form=form,
      user_db=user_db,
    )