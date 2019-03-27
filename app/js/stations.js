$(document).ready(function () {
    var stations = $('#stations');
    var template = $('#template').html();

    $.ajax({
        url: '/json/stations',
        type: 'GET',
        dataType: 'json'
    })
        .done(function (data) {
            var rendered = Mustache.render(template, data);
            stations.html(rendered);
            stations.removeClass('hidden');
            $('#loading').addClass('hidden');
        })
        .fail(function (data, status, error) {
        })
});
