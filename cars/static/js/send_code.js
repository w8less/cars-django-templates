function send_code() {
  let csrf_token = $('[name="csrfmiddlewaretoken"]')[0].value;
  $('#code-button').attr('disabled', true).text('Отправка..');
  $.ajax({
    url: '/auth/send_code/',
    type: 'POST',
    data: { phone: $('#phone').val(), csrfmiddlewaretoken: csrf_token },
  })
  .done(function() {
    $('#phone').removeClass('is-invalid');
    $('#code-button').text('Код отправлен. Ожидайте СМС');
  })
  .fail(function() {
    $('#phone').addClass('is-invalid');
    $('#code-button').attr('disabled', false).text('Отправить код подтверждения');
  });
}