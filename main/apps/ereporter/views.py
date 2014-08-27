# coding: utf-8
import datetime

from google.appengine.api import namespace_manager
from google.appengine.ext.ereporter import report_generator
from google.appengine.ext import db
import flask

from apps import auth
from apps.user.models import User
import config


bpa = flask.Blueprint(
    'ereporter',
    __name__,
    url_prefix='/_s/ereporter'
  )


@bpa.route('/')
@auth.cron_required
def send_reports():
  if not config.CONFIG_DB.send_error_reports or not config.CONFIG_DB.feedback_email:
    return 'Sending error reports is disabled'
  recipients = User.query(
      User.admin == True,
      User.active == True,
      User.email != '',
      User.permissions == 'send_error_reports'
    )
  if not recipients.count():
    return 'Recipients for error reports not found'

  rg = report_generator.ReportGenerator()
  rg.sender = config.CONFIG_DB.feedback_email
  rg.version_filter = 'all'
  rg.yesterday = datetime.date.today() - datetime.timedelta(days=1)
  rg.app_id = config.APPLICATION_ID
  rg.major_version = config.CURRENT_VERSION_MAJOR
  rg.minor_version = int(config.CURRENT_VERSION_MINOR)
  rg.max_results = rg.DEFAULT_MAX_RESULTS

  namespace_manager.set_namespace('')
  try:
    exceptions = rg.GetQuery(order='-minor_version').fetch(rg.max_results)
  except db.NeedIndexError:
    exceptions = rg.GetQuery().fetch(rg.max_results)

  if exceptions:
    report = rg.GenerateReport(exceptions)
    for recipient in recipients:
      rg.to = recipient.email
      rg.SendReport(report)
  return 'Ok'
