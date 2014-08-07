# coding: utf-8
from flask.ext import wtf

from apps.auth.decorators import permission_registered
from core import util


###############################################################################
# User Update
###############################################################################
class UserUpdateForm(wtf.Form):
  username = wtf.StringField(
      'Username',
      [wtf.validators.required(), wtf.validators.length(min=3)],
      filters=[util.email_filter],
    )
  name = wtf.StringField(
      'Name',
      [wtf.validators.required()], filters=[util.strip_filter],
    )
  email = wtf.StringField(
      'Email',
      [wtf.validators.optional(), wtf.validators.email()],
      filters=[util.email_filter],
    )
  admin = wtf.BooleanField('Admin')
  active = wtf.BooleanField('Active')
  permissions = wtf.SelectMultipleField(
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
  user_key = wtf.StringField('User Key', [wtf.validators.required()])
  user_keys = wtf.StringField('User Keys', [wtf.validators.required()])
  username = wtf.StringField('Username', [wtf.validators.optional()])
  name = wtf.StringField(
      'Name (merged)',
      [wtf.validators.required()], filters=[util.strip_filter],
    )
  email = wtf.StringField(
      'Email (merged)',
      [wtf.validators.optional(), wtf.validators.email()],
      filters=[util.email_filter],
    )


###############################################################################
# Profile stuff
###############################################################################
class ProfileUpdateForm(wtf.Form):
  name = wtf.StringField(
      'Name',
      [wtf.validators.required()], filters=[util.strip_filter],
    )
  email = wtf.StringField(
      'Email',
      [wtf.validators.optional(), wtf.validators.email()],
      filters=[util.email_filter],
    )
