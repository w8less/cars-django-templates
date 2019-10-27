function pay () {
  let csrf_token = $('[name="csrfmiddlewaretoken"]')[0].value;
  let plan = $('input[name=plan]:checked')[0].value;
  $.ajax({
    url: '/order/set/',
    type: 'POST',
    data: { plan: plan, csrfmiddlewaretoken: csrf_token },
  })
  .done(function(response) {
    $('.modal-footer').append('<div class="liqpay" style="display: none;"></div>');
    $('.liqpay').append(response['button']);
    $('input[name=btn_text]').trigger('click');
  })
  .fail(function(response) {
    // alert(response.responseText['phone']);
    // if (response.responseText['phone']) {
    // }
  });
}