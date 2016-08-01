function getLocation(position) {
    console.log("(" + position.coords.latitude + ", " + position.coords.longitude + ")");
}

navigator.geolocation.getCurrentPosition(getLocation);

