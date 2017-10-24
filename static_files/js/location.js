function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else { 
        x.innerHTML = "Geolocation is not supported by this browser.";
    }
}

function showPosition(position) {
    $('#lat_container').attr('value', position.coords.latitude);
    $('#lon_container').attr('value', position.coords.longitude);
}

$(document).ready(function(){
    getLocation();
});
