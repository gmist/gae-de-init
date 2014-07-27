# coding: utf-8
import flask

from apps import auth
from core import task
import config
import forms

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
  return flask.render_template('pages/welcome.html', html_class='welcome')


###############################################################################
# Feedback page
###############################################################################
@bp.route('/feedback/', methods=['GET', 'POST'])
def feedback():
  if not config.CONFIG_DB.feedback_email:
    return flask.abort(418)

  form = forms.FeedbackForm(obj=auth.current_user_db())
  if form.validate_on_submit():
    body = '%s\n\n%s' % (form.message.data, form.email.data)
    kwargs = {'reply_to': form.email.data} if form.email.data else {}
    task.send_mail_notification(form.subject.data, body, **kwargs)
    flask.flash('Thank you for your feedback!', category='success')
    return flask.redirect(flask.url_for('pages.welcome'))

  return flask.render_template(
      'pages/feedback.html',
      title='Feedback',
      html_class='feedback',
      form=form,
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
