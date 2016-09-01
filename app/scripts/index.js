$(document).ready(
    function () {
        navigator.geolocation.getCurrentPosition(getLocation);
    }
);

function getLocation(position) {
    getTides(
        position.coords.latitude.toPrecision(6) +
        "," +
        position.coords.longitude.toPrecision(6)
    );
}

function getTides(location_string) {
    $("#tides").removeClass("hidden");
    $('#loading')
        .empty()
        .append('<p>Loading<br/>(' + location_string + ')</p>')
    ;

    $.ajax(
        {
            url: '/json/tides',
            data: 'loc=' + location_string,
            type: 'GET',
            dataType: 'json'
        }
    )
     .done(
         function (data) {
             var template = $("#tides-template").html();
             data.lower = function () {
                 return function (text, render) {
                     return render(text).toLowerCase();
                 }
             };
             var rendered = Mustache.render(template, data);
             $("#tides-data")
                 .html(rendered)
                 .removeClass("hidden")
             ;
             $('#loading').addClass("hidden");
         }
     )
     .fail(
         function (data, status, error) {
             build_error(data, error);
         }
     )
}

function getStations() {
    $.ajax(
        {
            url: '/json/stations',
            type: 'GET',
            dataType: 'json'
        }
    )
     .done(
         function (data) {
             var template = $('#stations-template').html();
             var rendered = Mustache.render(template, data);
             $('#stations-data')
                 .html(rendered)
                 .removeClass('hidden')
             ;
             $('#loading').addClass('hidden');
         }
     )
     .fail(
         function (data, status, error) {
         }
     )
}

function build_error(data, error) {
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