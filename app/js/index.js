var tides_template = $("#tides-template").html();
var stations_template = $('#stations-template').html();
var error_template = $('#error-template').html();

var cur_pos = {};

$(document).ready(function () {
    var Router = Backbone.Router.extend(
        {
            routes: {
                "": "tides",
                "stations": "stations"
            }
        }
    );
    var router = new Router;

    router.on({
        'route:tides': function () {
            getLocationAndTides();
        },
        'route:stations': function () {
            getStations();
        }
    });


    // Start Backbone history, a necessary step for bookmarkable URL's
    Backbone.history.start();
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
    $('#loading')
        .empty()
        .append('<p>Loading tides for<br/>(' + location_string + ')...</p>')
        .removeClass("hidden")
    ;
    $("#stations").addClass("hidden");
    $("#error").addClass("hidden");

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
             data.lower = function () {
                 return function (text, render) {
                     return render(text).toLowerCase();
                 }
             };
             var rendered = Mustache.render(tides_template, data);
             $("#tides")
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
    $('#loading')
        .empty()
        .append('<p>Loading stations list...</p>')
        .removeClass("hidden")
    ;
    $("#tides").addClass("hidden");
    $("#error").addClass("hidden");

    $.ajax(
        {
            url: '/json/stations',
            type: 'GET',
            dataType: 'json'
        }
    )
     .done(
         function (data) {
             var rendered = Mustache.render(stations_template, data);
             $('#stations')
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
    var loading = $('#loading');
    loading
        .empty()
        .append('<p>Analyzing error...</p>')
        .removeClass("hidden")
    ;
    $("#tides").addClass("hidden");
    $("#stations").addClass("hidden");

    var data = {
        status: JSON.parse(err_data.responseText)['msg'],
        error: error
    };

    var rendered = Mustache.render(error_template, data);
    $('#error')
        .html(rendered)
        .removeClass('hidden')
    ;
    loading.addClass('hidden');
}