# coding: utf-8
from google.appengine.ext import ndb
import flask

import config
from apps import auth
from core import task
from core import util
import forms
import models


bpa = flask.Blueprint(
    'feedback.admin',
    __name__,
    url_prefix='/feedback/admin',
    template_folder='templates'
  )

bp = flask.Blueprint(
    'feedback',
    __name__,
    url_prefix='/feedback',
    template_folder='templates',
  )


@bpa.route('/', endpoint='list')
@auth.admin_required
def admin_list():
  feedback_dbs, next_cursor, prev_cursor = models.Feedback.get_dbs()

  return flask.render_template(
      'feedback/admin/list.html',
      html_class='feedback-list',
      title='Feedback List',
      feedback_dbs=feedback_dbs,
      next_url=util.generate_next_url(next_cursor),
      prev_url=util.generate_next_url(prev_cursor),
      api_url=flask.url_for('api.feedbacks'),
    )


@bpa.route('/<int:feedback_id>/show/', methods=['GET', 'POST'], endpoint='show')
@auth.admin_required
def admin_show(feedback_id):
  feedback_db = models.Feedback.get_by_id(feedback_id)
  if not feedback_db.is_read and flask.request.method == 'GET':
    feedback_db.is_read = True
    feedback_db.put()
  form = forms.FeedbackForm(obj=feedback_db)
  if form.validate_on_submit():
    form.populate_obj(feedback_db)
    feedback_db.put()
    return flask.redirect(
        flask.url_for('feedback.admin.list', is_read=False))
  return flask.render_template(
      'feedback/admin/show.html',
      title='Show Feedback',
      html_class='feedback-show',
      form=form,
      feedback_db=feedback_db,
      api_url=flask.url_for('api.feedback', key=feedback_db.key.urlsafe())
  )


@bp.route('/', methods=['GET', 'POST'])
def index():
  if not config.CONFIG_DB.feedback_email:
    return flask.abort(418)

  form = forms.FeedbackForm(obj=auth.current_user_db())
  if form.validate_on_submit():
    feedback_obj = models.Feedback()
    form.populate_obj(feedback_obj)
    feedback_obj.user = auth.current_user_key()
    feedback_obj.put()
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
