$("#geolocation_button").click(function () {
    console.log("asdasd");
    origin = $("#id_origin");
    origin.attr("placeholder", "");
    origin.addClass('loaderbg');

    if (navigator.geolocation)
        navigator.geolocation.getCurrentPosition(successCallback, errorCallback_highAccuracy, {
            maximumAge: 600000,
            timeout: 5000,
            enableHighAccuracy: true
        });
});

function successCallback(position) {

    var latitude = position.coords.latitude;
    var longitude = position.coords.longitude;
    var coords = [latitude, longitude];
    $.ajax({
                    method: "GET",
                    url: "https://nominatim.openstreetmap.org/reverse",
                    data: {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude,
                        format: "jsonv2"
                    },
                      success: function(data) {
                        origin.removeClass("loaderbg");
                        origin.prop('disabled', true);
                        $("#id_coordinates").val(coords);
                        origin.val(data['address']['road'] + " " + data['address']['house_number']);
                        let acc = position.coords.accuracy;
                        console.log("Posisiton: \n%f,%f", latitude, longitude);
                        console.log("Accuracy: ", acc);

                      },
                    error(data){
                        error("Error");
                    }
                });
}

function errorCallback_highAccuracy(error) {
    if (error.code === error.TIMEOUT)
    {
        console.log("attempting to get low accuracy location");
        navigator.geolocation.getCurrentPosition(
               successCallback,
               errorCallback_lowAccuracy,
               {maximumAge:600000, timeout:10000, enableHighAccuracy: false});
        return;
    }

    var msg = "<p>Can't get your location (high accuracy attempt). Error = ";
    if (error.code === 1)
        msg += "PERMISSION_DENIED";
    else if (error.code === 2)
        msg += "POSITION_UNAVAILABLE";
    msg += ", msg = "+error.message;

    console.log(msg);
}


function errorCallback_lowAccuracy(error) {
    var msg = "<p>Can't get your location (low accuracy attempt). Error = ";
    if (error.code === 1)
        msg += "PERMISSION_DENIED";
    else if (error.code = 2)
        msg += "POSITION_UNAVAILABLE";
    else if (error.code === 3)
        msg += "TIMEOUT";
    msg += ", msg = " + error.message;
    console.log(msg);
}
