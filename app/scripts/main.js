
$(document).ready( function () {
    navigator.geolocation.getCurrentPosition(getLocation);
});

function getLocation(position) {
    var location_string = position.coords.latitude + "," + position.coords.longitude;
    console.log(location_string);

    $.ajax({
        url: '/json/tides',
        data: 'loc=' + location_string,
        type: 'GET',
        dataType: 'json'
    })
        .done(function (json_data) {
            console.log(json_data);
        })
        .fail(function (xhr, status, errorThrown) {
            console.log(xhr, status, errorThrown);
        })
}
