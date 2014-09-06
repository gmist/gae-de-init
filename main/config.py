# coding: utf-8

import os


PRODUCTION = os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Eng')
DEBUG = DEVELOPMENT = not PRODUCTION

try:
  # This part is surrounded in try/except because the config.py file is
  # also used in the run.py script which is used to compile/minify the client
  # side files (*.less, *.coffee, *.js) and is not aware of the GAE
  from google.appengine.api import app_identity
  APPLICATION_ID = app_identity.get_application_id()
except (ImportError, AttributeError):
  pass
else:
  from datetime import datetime
  CURRENT_APPLICATION_ID = os.environ['APPLICATION_ID']
  CURRENT_VERSION_ID = os.environ.get('CURRENT_VERSION_ID')
  CURRENT_VERSION_MAJOR, CURRENT_VERSION_MINOR = CURRENT_VERSION_ID.rsplit('.', 1)
  CURRENT_VERSION_NAME = CURRENT_VERSION_ID.split('.')[0]
  CURRENT_VERSION_TIMESTAMP = long(CURRENT_VERSION_ID.split('.')[1]) >> 28
  if DEVELOPMENT:
    import calendar
    CURRENT_VERSION_TIMESTAMP = calendar.timegm(datetime.utcnow().timetuple())
  CURRENT_VERSION_DATE = datetime.utcfromtimestamp(CURRENT_VERSION_TIMESTAMP)

  from apps.admin import models

  CONFIG_DB = models.Config.get_master_db()
  SECRET_KEY = CONFIG_DB.flask_secret_key.encode('ascii')
  RECAPTCHA_PUBLIC_KEY = CONFIG_DB.recaptcha_public_key
  RECAPTCHA_PRIVATE_KEY = CONFIG_DB.recaptcha_private_key
  RECAPTCHA_OPTIONS = ''

DEFAULT_DB_LIMIT = 64


###############################################################################
# Client modules, also used by the run.py script.
###############################################################################
STYLES = [
    'src/style/style.less',
  ]

SCRIPTS = [
    ('libs', [
        'ext/js/jquery/jquery.js',
        'ext/js/moment/moment.js',
        'ext/js/nprogress/nprogress.js',
        'ext/js/bootstrap/alert.js',
        'ext/js/bootstrap/button.js',
        'ext/js/bootstrap/transition.js',
        'ext/js/bootstrap/collapse.js',
        'ext/js/bootstrap/dropdown.js',
        'ext/js/bootstrap/tooltip.js',
      ]),
    ('core', [
        'src/script/core/service.coffee',
        'src/script/core/util.coffee',
      ]),
    ('apps', [
        'src/script/apps/admin/admin.coffee',
        'src/script/apps/auth/signin.coffee',
        'src/script/apps/feedback/admin.coffee',
        'src/script/apps/user/admin.coffee',
        'src/script/apps/user/profile.coffee',
        'src/script/apps/init.coffee',
      ]),
  ]
