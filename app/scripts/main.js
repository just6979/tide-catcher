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
    var table = $("#tides");
    table.append(
        '<caption id="top_caption" class="top">\n' +
        _.escape(data['resp_station']) +
        '</caption>'
    );
    _.each(data['tides'], function (tide) {
        table.append(
            '<tr class="' +
            _.escape(tide['type']).toLowerCase() + ' ' +
            _.escape(tide['prior']).toLowerCase() + '">\n' +
            '<td class="type">' + _.escape(tide['type']) + '</td>\n' +
            '<td class="date">' + _.escape(tide['date']) + '</td>\n' +
            '<td class="day">' + _.escape(tide['day']) + '</td>\n' +
            '<td class="time">' + _.escape(tide['time']) + '</td>\n' +
            '</tr>\n'
        );
    });

    $('#req_loc').text(data['req_lat'] + ', ' + data['req_lon']);
    $('#req_time').text(
        data['req_timestamp']['date'] + ' ' +
        data['req_timestamp']['day'] + ' ' +
        data['req_timestamp']['time']
    );
    $('#resp_loc').text(data['resp_lat'] + ', ' + data['resp_lon']);
    $('#resp_tz').text(data['tz_name'] + ', UTC' + data['tz_offset']);

    $('#loading').addClass('hidden');
    $('#tides').removeClass('hidden');
    $('#info').removeClass('hidden');
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