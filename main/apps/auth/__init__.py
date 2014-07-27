# coding: utf-8
from werkzeug import utils as werk_utils

from decorators import admin_required
from decorators import login_required
from decorators import permission_required

from login_manager import current_user_db
from login_manager import current_user_id
from login_manager import current_user_key
from login_manager import is_logged_in


def load_providers_config():
  providers = []
  for pkg in werk_utils.find_modules('%s.providers' % __package__, True):
    cfg = werk_utils.import_string('%s.CONFIG' % pkg, True)
    if cfg:
        providers.append(cfg)
  return providers

PROVIDERS_CONFIG = load_providers_config()
del load_providers_config


def register_providers(app):
  for pkg in werk_utils.find_modules('%s.providers' % __package__, True):
    bp = werk_utils.import_string('%s.views.bp' % pkg, True)
    if bp:
      app.register_blueprint(bp)
    bps = werk_utils.import_string('%s.views.bps' % pkg, True)
    if bps:
      app.register_blueprint(bps)


def app_init(app):
  from login_manager import login_manager as lm
  lm.init_app(app)
  import apps.user.forms

  register_providers(app)
