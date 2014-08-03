# coding: utf-8
from google.appengine.api import app_identity
import flask

from apps import auth
from core import util
import config
import forms
import models


bp = flask.Blueprint(
    'admin',
    __name__,
    url_prefix='/admin',
    template_folder='templates',
  )

bps = flask.Blueprint(
    'admin.service',
    __name__,
    url_prefix='/_s/admin',
  )


@bp.route('/')
@auth.admin_required
def index():
  return flask.render_template('admin/index.html')


@bps.route('/config/')
@bp.route('/config/', methods=['GET', 'POST'])
@auth.admin_required
def config_update():
  config_db = models.Config.get_master_db()
  form = forms.ConfigUpdateForm(obj=config_db)

  if form.validate_on_submit():
    form.populate_obj(config_db)
    if not config_db.flask_secret_key:
      config_db.flask_secret_key = util.uuid()
    config_db.put()
    reload(config)
    flask.current_app.config.update(CONFIG_DB=config_db)
    return flask.redirect(flask.url_for('pages.welcome'))

  if flask.request.path.startswith('/_s/'):
    return util.jsonify_model_db(config_db)

  instances_url = None
  if config.PRODUCTION:
    instances_url = '%s?app_id=%s&version_id=%s' % (
        'https://appengine.google.com/instances',
        app_identity.get_application_id(),
        config.CURRENT_VERSION_ID,
      )

  return flask.render_template(
      'admin/config_update.html',
      title='App Config',
      html_class='admin-config',
      form=form,
      config_db=config_db,
      instances_url=instances_url,
      has_json=True,
    )
