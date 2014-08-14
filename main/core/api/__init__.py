# coding: utf-8
from datetime import datetime
from flask.ext import restful
import funcy

from core import util


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


