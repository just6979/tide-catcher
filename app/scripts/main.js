$(document).ready(function () {
    navigator.geolocation.getCurrentPosition(getLocation);
});

function getLocation(position) {
    var location_string = position.coords.latitude.toPrecision(6) + "," + position.coords.longitude.toPrecision(6);

    $('#loading').empty().append('<p>Loading<br/>(' + location_string + ')</p>');

    $.ajax({
        url: '/json/tides',
        data: 'loc=' + location_string,
        type: 'GET',
        dataType: 'json'
    })
        .done(function (data) {
            build_table(data);
        })
        .fail(function (data, status, error) {
           build_error(data, error);
        })
}

function build_table(data) {
    data.lower = function () {
        return function (text, render) {
            //wrong line return render(text.toLowerCase());
            return render(text).toLowerCase();
        }
    };
    var content = $("#content");
    var template = $("#template").html();
    var rendered = Mustache.render(template, data);
    content.html(rendered);
}

function build_error (data, error) {
    console.log(data);
    var content = $('#content');
    var output;

    if (data.responseText != null) {
        output = 'Error: ' + data.responseText;
    } else {
        output = 'Error: ' + data.status + ' - ' + error;
    }

    $('#loading').addClass('hidden');

    content.append('<p>' + _.escape(output) + '</p>');
}