# coding: utf-8
import flask

from core import util
import config


bp = flask.Blueprint(
    'pages',
    __name__,
    template_folder='templates',
  )


###############################################################################
# Main page
###############################################################################
@bp.route('/')
def welcome():
  return flask.render_template(
      'pages/welcome.html',
      html_class='welcome',
      meta=util.make_meta(
          description='''
              gae-init is the easiest way to start new web
              applications on Google App Engine.'''
        )
    )


###############################################################################
# Sitemap stuff
###############################################################################
@bp.route('/sitemap.xml')
def sitemap():
  response = flask.make_response(flask.render_template(
      'pages/sitemap.xml',
      host_url=flask.request.host_url[:-1],
      lastmod=config.CURRENT_VERSION_DATE.strftime('%Y-%m-%d'),
    ))
  response.headers['Content-Type'] = 'application/xml'
  return response


###############################################################################
# Warmup request
###############################################################################
@bp.route('/_ah/warmup')
def warmup():
  # TODO: put your warmup code here
  return 'success'
