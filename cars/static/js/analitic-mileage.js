$('.Search').on('click', function (e) {
  let modelValue = $('#filter_model option:selected').val();
  let modelName = $('#filter_model option:selected').text();
  let markName = $('#filter_brand option:selected').text();
  if (modelValue) {
    e.preventDefault();
    let csrf_token = $('[name="csrfmiddlewaretoken"]')[0].value;
    $.ajax({
      url: '/analitic/mileage/',
      type: 'post',
      data: { 'model': modelValue , csrfmiddlewaretoken: csrf_token },
      success: function (response) {
        $('.graph').css('display', 'block');
        let years = response['years']
        let fuels = response['fuels']
        let dataSets = []
        for (fuel in fuels) {
          let mydict = {
            'label': fuel,
            'data': fuels[fuel],
            //'backgroundColor': $.Color([ 255, 0, 100 ]),
            //'hoverBackgroundColor': this.convertHex(rgb(100,200,255), 70),
          }
          dataSets.push(mydict)
        }
        let chartData = {
          labels: years,
          datasets: dataSets
        };
        let chLine = $('#chLine');
        if (chLine) {
          new Chart(chLine, {
            type: 'line',
            data: chartData,
            options: {
              title: {
                display: true,
                text: 'Статистика пробега по годам ' + markName + ' ' + modelName,
                position: 'top'
              },
              scales: {
                yAxes: [{
                  ticks: {
                    beginAtZero: true
                  }
                }]
              },
              legend: {
                display: true
              }
            }
          });
        }
      }
    })
  };
});