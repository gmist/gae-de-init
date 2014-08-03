# coding: utf-8
import flask

import config
from apps import auth
from core import task
import forms


bp = flask.Blueprint(
    'feedback',
    __name__,
    url_prefix='/feedback',
    template_folder='templates',
  )


@bp.route('/', methods=['GET', 'POST'])
def index():
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
      'feedback/index.html',
      title='Feedback',
      html_class='feedback',
      form=form,
    )
