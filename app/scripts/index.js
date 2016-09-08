var cur_pos = {};

$(document).ready(function () {
    getLocationAndTides()
});

function getLocationAndTides() {
    function geo_success(position) {
        cur_pos = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
        };
        getTides();
    }

    function geo_error(error) {
        var data, message;
        switch (error.code) {
        case 1:
            data = {status: "PERMISSION_DENIED"};
            message = "No permission to access location data.";
            break;
        case 2:
            data = {status: "POSITION_UNAVAILABLE"};
            message = "Internal error acquiring location data.";
            break;
        case 3:
            data = {status: "TIMEOUT"};
            message = "No location data acquired in the time allotted.";
            break;
        }
        build_error(data, message);
    }

    var geo_options = {
        enableHighAccuracy: true,
        maximumAge: 30000,
        timeout: 5000
    };

    navigator.geolocation.getCurrentPosition(geo_success, geo_error, geo_options);
}

function getTides() {
    var location_string = cur_pos.latitude.toPrecision(6) + "," + cur_pos.longitude.toPrecision(6);
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

function build_error(err_data, error) {
    var status;

    if (err_data.responseText != null) {
        status = err_data.responseText;
    } else {
        status = err_data.status;
    }

    var data = {
        status: status,
        error: error
    };

    var template = $('#error-template').html();
    var rendered = Mustache.render(template, data);
    $('#error')
        .html(rendered)
        .removeClass('hidden')
    ;
    $('#loading').addClass('hidden');
}