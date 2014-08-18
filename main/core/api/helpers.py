# coding: utf-8
from datetime import datetime
import logging
from core.util import get_module_obj

from flask.ext import restful
from werkzeug import exceptions
from werkzeug import utils as w_utils
import flask
import funcy

from core import util


class Api(restful.Api):
  def unauthorized(self, response):
    flask.abort(401)

  def handle_error(self, e):
    logging.exception(e)
    try:
      e.code
    except AttributeError:
      e.code = 500
      e.name = e.description = 'Internal Server Error'
    return util.jsonpify({
        'status': 'error',
        'error_code': e.code,
        'error_name': util.slugify(e.name),
        'error_message': e.name,
        'error_class': e.__class__.__name__,
        'description': e.description,
      }), e.code


def make_response(data, marshal_table, next_cursor=None, prev_cursor=None):
  if funcy.is_seqcoll(data):
    response = {
        'status': 'success',
        'count': len(data),
        'now': datetime.utcnow().isoformat(),
        'result': map(lambda l: restful.marshal(l, marshal_table), data),
      }
    if next_cursor:
      response['next_cursor'] = next_cursor
      response['next_url'] = util.generate_next_url(next_cursor)
    if prev_cursor:
      response['prev_cursor'] = prev_cursor,
      response['prev_url'] = util.generate_next_url(prev_cursor)
    return response
  return {
      'status': 'success',
      'now': datetime.utcnow().isoformat(),
      'result': restful.marshal(data, marshal_table)
    }


def make_not_found_exception(description):
  exception = exceptions.NotFound()
  exception.description = description
  raise exception


def register_api(api):
  for pkg in w_utils.find_modules('apps', True):
    pkg_api = '%s.api' % pkg
    resources = get_module_obj(pkg_api, 'API')
    if not resources:
      continue
    for resource in resources:
      register_api_resource(api, resource)


def register_api_resource(api, resource):
  if funcy.is_seqcoll(resource):
    cls, url, endpoint = (
        funcy.first(resource),
        funcy.second(resource),
        funcy.nth(2, resource),
      )
    api.add_resource(cls, url, endpoint=endpoint)
