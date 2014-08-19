window.init_feedback_list = ->
  init_feedback_selections()
  init_feedback_delete_btn()


init_feedback_selections = ->
  $('input[name=feedback_db]').each ->
    feedback_select_row $(this)

  $('#select-all').change ->
    $('input[name=feedback_db]').prop 'checked', $(this).is ':checked'
    $('input[name=feedback_db]').each ->
      feedback_select_row $(this)

  $('input[name=feedback_db]').change ->
    feedback_select_row $(this)


feedback_select_row = ($element) ->
  update_feedback_selections()
  $('input[name=feedback_db]').each ->
    id = $element.val()
    $("##{id}").toggleClass 'warning', $element.is ':checked'


update_feedback_selections = ->
  selected = $('input[name=feedback_db]:checked').length
  $('#feedback-actions').toggleClass 'hidden', selected == 0
  if selected is 0
    $('#select-all').prop 'indeterminate', false
    $('#select-all').prop 'checked', false
  else if $('input[name=feedback_db]:not(:checked)').length is 0
    $('#select-all').prop 'indeterminate', false
    $('#select-all').prop 'checked', true
  else
    $('#select-all').prop 'indeterminate', true


###############################################################################
# Delete Users Stuff
###############################################################################
init_feedback_delete_btn = ->
  $('#feedback-delete').click (e) ->
    clear_notifications()
    e.preventDefault()
    confirm_message = ($(this).data 'confirm').replace '{feedbacks}', $('input[name=feedback_db]:checked').length
    if confirm confirm_message
      feedback_keys = []
      $('input[name=feedback_db]:checked').each ->
        $(this).attr 'disabled', true
        feedback_keys.push $(this).val()
      delete_url = $(this).data 'service-url'
      success_message = $(this).data 'success'
      error_message = $(this).data 'error'
      service_call 'DELETE', delete_url, {feedback_keys: feedback_keys.join(',')}, (err, result) ->
        if err
          $('input[name=feedback_db]:disabled').removeAttr 'disabled'
          show_notification error_message.replace('{feedbacks}', feedback_keys.length), 'danger'
          return
        $("##{result.join(', #')}").fadeOut ->
          $(this).remove()
          update_feedback_selections()
          show_notification success_message.replace('{feedbacks}', feedback_keys.length), 'success'


