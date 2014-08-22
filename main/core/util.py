# coding: utf-8
from uuid import uuid4
import re
import unicodedata
import urllib

from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import ndb

from werkzeug import utils as w_utils
import flask
import funcy


###############################################################################
# Request Parameters
###############################################################################
def param(name, cast=None):
  value = None
  if flask.request.json:
    return flask.request.json.get(name, None)

  if value is None:
    value = flask.request.args.get(name, None)
  if value is None and flask.request.form:
    value = flask.request.form.get(name, None)

  if cast and value is not None:
    if cast is bool:
      return value.lower() in ['true', 'yes', '1', '']
    if cast is list:
      return value.split(',') if len(value) > 0 else []
    return cast(value)
  return value


def get_referrer_url():
  referrer = flask.request.referrer
  if referrer and referrer.startswith(flask.request.host_url):
    return referrer
  return None


def get_next_url(option_url=None, skip_referrer=False):
  next_url = param('next')
  if next_url:
    return next_url
  if not skip_referrer:
    referrer = get_referrer_url()
    if referrer:
      return referrer
  if option_url:
    return option_url
  return flask.url_for('pages.welcome')


###############################################################################
# Model manipulations
###############################################################################
def get_dbs(
    query, order=None, limit=None, cursor=None, keys_only=None, **filters
  ):
  '''Retrieves entities from datastore, by applying cursor pagination
  and equality filters. Returns dbs or keys and more cursor value
  '''
  limit = limit or flask.current_app.config.get('DEFAULT_DB_LIMIT')
  cursor = Cursor.from_websafe_string(cursor) if cursor else None
  model_class = ndb.Model._kind_map[query.kind]
  query_reverse = query
  query_forward = query
  if order:
    for o in order.split(','):
      if o.startswith('-'):
        query_reverse = query_reverse.order(model_class._properties[o[1:]])
        query_forward = query_forward.order(-model_class._properties[o[1:]])
      else:
        query_reverse = query_reverse.order(-model_class._properties[o])
        query_forward = query_forward.order(model_class._properties[o])

  for prop in filters:
    if filters.get(prop, None) is None:
      continue
    if funcy.is_seqcoll(filters[prop]):
      for value in filters[prop]:
        query_reverse = query_reverse.filter(model_class._properties[prop] == value)
        query_forward = query_forward.filter(model_class._properties[prop] == value)
    else:
      query_reverse = query_reverse.filter(model_class._properties[prop] == filters[prop])
      query_forward = query_forward.filter(model_class._properties[prop] == filters[prop])

  model_dbs, next_cursor, more = query_forward.fetch_page(
      limit, start_cursor=cursor, keys_only=keys_only,
    )
  model_dbs_prev, prev_cursor, rev_more = query_reverse.fetch_page(
      limit, start_cursor=cursor.reversed() if cursor else None, keys_only=True
    )
  next_cursor = next_cursor.urlsafe() if more else None
  prev_cursor = prev_cursor.reversed().urlsafe() if prev_cursor and cursor else None
  return list(model_dbs), next_cursor, prev_cursor


def get_keys(*arg, **kwargs):
  return get_dbs(*arg, keys_only=True, **kwargs)


@ndb.transactional(xg=True)
def delete_dbs(db_keys):
  ndb.delete_multi(db_keys)


###############################################################################
# JSON Response Helpers
###############################################################################
def jsonpify(*args, **kwargs):
  if param('callback'):
    content = '%s(%s)' % (
        param('callback'), flask.jsonify(*args, **kwargs).data,
      )
    mimetype = 'application/javascript'
    return flask.current_app.response_class(content, mimetype=mimetype)
  return flask.jsonify(*args, **kwargs)


###############################################################################
# Helpers
###############################################################################
def check_form_fields(*fields):
  fields_data = []
  for field in fields:
    if funcy.is_seqcoll(field):
      fields_data.extend([field.data for field in field])
    else:
      fields_data.append(field.data)
  return all(fields_data)


def make_meta(keywords=None, description=None, author=None):
  meta = {}
  if not keywords and description:
    keywords = description
  if keywords:
    if isinstance(keywords, (str, unicode)):
      keywords = re.sub(r'[\W_]+', ', ', keywords)
    if funcy.is_seqcoll(keywords):
      keywords = u', '.join(keywords)
    meta['keywords'] = keywords
  if description:
    if isinstance(description, (str, unicode)):
      description = description.strip()
    meta['description'] = description
  if author:
    meta['author'] = author
  return meta


def generate_next_url(next_cursor, base_url=None, cursor_name='cursor'):
  '''Substitutes or alters the current request URL with a new cursor parameter
  for next page of results
  '''
  if not next_cursor:
    return None
  base_url = base_url or flask.request.base_url
  args = flask.request.args.to_dict()
  args[cursor_name] = next_cursor
  return '%s?%s' % (base_url, urllib.urlencode(args))


def uuid():
  return uuid4().hex


_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


def slugify(text):
  if not isinstance(text, unicode):
    text = unicode(text)
  text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
  text = unicode(_slugify_strip_re.sub('', text).strip().lower())
  return _slugify_hyphenate_re.sub('-', text)


_username_re = re.compile(r'^[a-z0-9]+(?:[\.][a-z0-9]+)*$')


def is_valid_username(username):
  return True if _username_re.match(username) else False


def update_query_argument(name, value=None, ignore='cursor', is_list=False):
  ignore = ignore.split(',') if isinstance(ignore, str) else ignore or []
  arguments = {}
  for key, val in flask.request.args.items():
    if key not in ignore and (is_list and value is not None or key != name):
      arguments[key] = val
  if value is not None:
    if is_list:
      values = []
      if name in arguments:
        values = arguments[name].split(',')
        del arguments[name]
      if value in values:
        values.remove(value)
      else:
        values.append(value)
      if values:
        arguments[name] = ','.join(values)
    else:
      arguments[name] = value
  query = '&'.join('%s=%s' % item for item in sorted(arguments.items()))
  return '%s%s' % (flask.request.path, '?%s' % query if query else '')


def get_module_obj(pkg_views, obj_name):
  return w_utils.import_string('%s.%s' %(pkg_views, obj_name), True)


def register_apps(app):
  for pkg in w_utils.find_modules('apps', True):
    pkg_views = '%s.views' % pkg
    objs = [get_module_obj(pkg_views, obj) for obj in ['bpa', 'bp']]
    funcy.walk(funcy.silent(app.register_blueprint), objs)
    app_init = get_module_obj(pkg, 'app_init')
    if app_init:
      app_init(app)


###############################################################################
# Lambdas
###############################################################################
strip_filter = lambda x: x.strip() if x else ''
email_filter = lambda x: x.lower().strip() if x else ''
sort_filter = lambda x: sorted(x) if x else []
