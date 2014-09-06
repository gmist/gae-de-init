# coding: utf-8
import flask
import funcy

from core.api import helpers as restful
from core import util
import config


app = flask.Flask(__name__)
app.config.from_object(config)
app.jinja_env.line_statement_prefix = '#'
app.jinja_env.line_comment_prefix = '##'
app.jinja_env.globals.update(
    check_form_fields=util.check_form_fields,
    is_iterable=funcy.is_seqcoll,
    slugify=util.slugify,
    update_query_argument=util.update_query_argument,
  )

if config.DEVELOPMENT:
  from werkzeug import debug
  app.wsgi_app = debug.DebuggedApplication(app.wsgi_app, evalex=True)
  app.testing = True

util.register_apps(app)

api = restful.Api(app)
restful.register_api(api)


###############################################################################
# Error Handling
###############################################################################
@app.errorhandler(400)  # Bad Request
@app.errorhandler(401)  # Unauthorized
@app.errorhandler(403)  # Forbidden
@app.errorhandler(404)  # Not Found
@app.errorhandler(405)  # Method Not Allowed
@app.errorhandler(410)  # Gone
@app.errorhandler(418)  # I'm a Teapot
@app.errorhandler(500)  # Internal Server Error
def error_handler(e):
  logging.exception(e)
  try:
    e.code
  except AttributeError:
    e.code = 500
    e.name = 'Internal Server Error'

  if flask.request.path.startswith('/api/'):
    return api.handle_error(e)

  return flask.render_template(
      'error.html',
      title='Error %d (%s)!!1' % (e.code, e.name),
      html_class='error-page',
      error=e,
    ), e.code


if config.PRODUCTION:
  @app.errorhandler(Exception)
  def production_error_handler(e):
    return error_handler(e)


if config.CONFIG_DB.send_error_reports:
  import logging
  from google.appengine.ext import ereporter
  ereporter.register_logger()
