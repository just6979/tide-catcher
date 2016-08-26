$(document).ready(function () {
    navigator.geolocation.getCurrentPosition(getLocation);
});

function getLocation(position) {
    var location_string = position.coords.latitude + "," + position.coords.longitude;

    $('#loading').empty().append('Loading<br/>(' + location_string + ')');

    $.ajax({
        url: '/json/tides',
        data: 'loc=' + location_string,
        type: 'GET',
        dataType: 'json'
    })
        .done(function (json_data) {
            build_table(json_data);
        })
        .fail(function (xhr, status, errorThrown) {
            console.log(xhr, status, errorThrown);
        })
}

function build_table(data) {
    var table = $("#tides-table");
    table.append(
        '<caption id="top_caption" class="top">\n' +
        data['resp_station'] +
        '</caption>'
    );
    console.log(data['tides']);
    for (var i = 0; i < data['tides'].length; i++) {
        var tide = data['tides'][i];
        table.append(
            '<tr class="' + tide['type'].toLowerCase() + ' ' + tide['prior'].toLowerCase() + '">\n' +
            '<td class="type">' + tide['type'] + '</td>\n' +
            '<td class="date">' + tide['date'] + '</td>\n' +
            '<td class="day">' + tide['day'] + '</td>\n' +
            '<td class="time">' + tide['time'] + '</td>\n' +
            '</tr>\n'
        );
    }
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
