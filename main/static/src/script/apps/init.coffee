$ ->
  init_common()

$ -> $('html.welcome').each ->
  LOG('init welcome')

$ -> $('html.profile').each ->
  init_profile()

$ -> $('html.auth').each ->
  init_auth()

$ -> $('html.feedback').each ->

$ -> $('html.feedback-list').each ->
  init_feedback_list()

$ -> $('html.user-list').each ->
  init_user_list()

$ -> $('html.user-merge').each ->
  init_user_merge()

$ -> $('html.admin-config').each ->
  init_admin_config()
