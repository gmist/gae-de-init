# coding: utf-8
from flask.ext import wtf
import wtforms

from apps.auth.decorators import permission_registered
from core import util


###############################################################################
# User Update
###############################################################################
class UserUpdateForm(wtf.Form):
  username = wtforms.StringField(
      'Username',
      [wtforms.validators.required(), wtforms.validators.length(min=3)],
      filters=[util.email_filter],
    )
  name = wtforms.StringField(
      'Name',
      [wtforms.validators.required()], filters=[util.strip_filter],
    )
  email = wtforms.StringField(
      'Email',
      [wtforms.validators.optional(), wtforms.validators.email()],
      filters=[util.email_filter],
    )
  admin = wtforms.BooleanField('Admin')
  active = wtforms.BooleanField('Active')
  verified = wtforms.BooleanField('Verified')
  permissions = wtforms.SelectMultipleField(
      'Permissions',
      filters=[util.sort_filter],
    )

  _permission_choices = set()

  def __init__(self, *args, **kwds):
    super(UserUpdateForm, self).__init__(*args, **kwds)
    self.permissions.choices = [
        (p, p) for p in sorted(UserUpdateForm._permission_choices)
      ]

  @permission_registered.connect
  def _permission_registered_callback(sender, permission):
    UserUpdateForm._permission_choices.add(permission)


###############################################################################
# User Merge
###############################################################################
class UserMergeForm(wtf.Form):
  user_key = wtforms.StringField('User Key', [wtforms.validators.required()])
  user_keys = wtforms.StringField('User Keys', [wtforms.validators.required()])
  username = wtforms.StringField('Username', [wtforms.validators.optional()])
  name = wtforms.StringField(
      'Name (merged)',
      [wtforms.validators.required()], filters=[util.strip_filter],
    )
  email = wtforms.StringField(
      'Email (merged)',
      [wtforms.validators.optional(), wtforms.validators.email()],
      filters=[util.email_filter],
    )


###############################################################################
# Profile stuff
###############################################################################
class ProfileUpdateForm(wtf.Form):
  name = wtforms.StringField(
      'Name',
      [wtforms.validators.required()], filters=[util.strip_filter],
    )
  email = wtforms.StringField(
      'Email',
      [wtforms.validators.optional(), wtforms.validators.email()],
      filters=[util.email_filter],
    )


class ProfilePasswordForm(wtf.Form):
  old_password = wtforms.StringField(
      'Old Password', [wtforms.validators.optional()],
    )
  new_password = wtforms.StringField(
      'New Password',
      [wtforms.validators.required(), wtforms.validators.length(min=6)]
    )
