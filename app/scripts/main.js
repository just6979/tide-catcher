
$(document).ready( function () {
    navigator.geolocation.getCurrentPosition(getLocation);
});

function getLocation(position) {
    location_string = position.coords.latitude + "," + position.coords.longitude;
    console.log(location_string);
    $.ajax({
        url: '/json/tides?loc=' + location_string,
        type: 'GET',
        dataType: 'json'
    })
        .done(function (json_data) {
            console.log(json_data);
        });
}
