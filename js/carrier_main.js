// JavaScript
function generateMapWithMarkers() {

 var map = new google.maps.Map(document.getElementById('map-static'), {
            center: {lat: -34.397, lng: 150.644},
            zoom: 8
        });
    var pickupLocationInput = document.getElementById('pickup_location');
    var dropOffLocationInput = document.getElementById('drop_off_location');

    // Check if inputs exist and have values
    if (pickupLocationInput && dropOffLocationInput && pickupLocationInput.value && dropOffLocationInput.value) {
        var pickupLocation = pickupLocationInput.value.split(',');
        var dropOffLocation = dropOffLocationInput.value.split(',');

        // Convert coordinates to numbers
        var pointA = { lat: parseFloat(pickupLocation[0]), lng: parseFloat(pickupLocation[1]) };
        var pointB = { lat: parseFloat(dropOffLocation[0]), lng: parseFloat(dropOffLocation[1]) };

        // Calculate distance using Haversine formula or other methods
        var distance = calculateDistance(pointA, pointB); // Assuming you have a function to calculate distance

        $('#distance_display').html(Math.round(distance, 1))
        // Set zoom level based on distance
        var zoom = getZoomLevel(distance);

        // Define the markers
        var markers = [
            { position: pointA, label: 'A' }, // Marker A
            { position: pointB, label: 'B' } // Marker B
            // Add more markers as needed
        ];

        // Construct the URL for the Static Maps API
        var baseUrl = 'https://maps.googleapis.com/maps/api/staticmap';
        var apiKey = 'AIzaSyCWaQEjD36vYF2wHyocZl0DrkSkXBvTCvc'; // Replace with your actual API key
        var size = '455x400'; // Adjust the size of the image as needed
        var mapType = 'roadmap'; // Change the map type if needed
        var markerStyles = 'color:red'; // Adjust marker styles as needed

        var markersUrl = '';
        markers.forEach(marker => {
            markersUrl += `&markers=${marker.position.lat},${marker.position.lng}|label:${marker.label}|${markerStyles}`;
        });

        var mapUrl = `${baseUrl}?center=${pointA.lat},${pointA.lng}&zoom=${zoom}&size=${size}&maptype=${mapType}${markersUrl}&key=${apiKey}`;

        // Set the image source to the generated URL
        document.getElementById('map-static').src = mapUrl;
        calculateTimeBetweenPoints();
    } else {
        console.error('Pickup and drop-off locations are required.');
    }
}


function calculateDistance(pointA, pointB) {
    const earthRadiusKm = 6371; // Radius of the Earth in kilometers
    const dLat = degreesToRadians(pointB.lat - pointA.lat);
    const dLng = degreesToRadians(pointB.lng - pointA.lng);

    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(degreesToRadians(pointA.lat)) * Math.cos(degreesToRadians(pointB.lat)) *
              Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = earthRadiusKm * c;


    return distance;
}

function degreesToRadians(degrees) {
    return degrees * (Math.PI / 180);
}

function getZoomLevel(distance) {

    var zoomLevel = 10; // Default zoom level

    if (distance > 1000) {
        zoomLevel = 1; // Example zoom level for longer distances
    } else if (distance > 100) {
        zoomLevel = 5; // Example zoom level for medium distances
    }
    return zoomLevel;
}

 function loadMapScript() {
        var script = document.createElement('script');
        script.type = 'text/javascript';
        //script.src = 'https://maps.googleapis.com/maps/api/js?key=AIzaSyCk_5pj5OJufDsnZIx4YRHqlpz9fblcQ5o&libraries=places&callback=initMap';
        script.src = 'https://maps.googleapis.com/maps/api/js?key=AIzaSyCWaQEjD36vYF2wHyocZl0DrkSkXBvTCvc&libraries=places&callback=generateMapWithMarkers';
        document.body.appendChild(script);
    }

 if(document.getElementById('map-static')){
    // Load the map script when the page is loaded
    window.onload = loadMapScript;
}


var ratingForm = document.getElementById('ratingForm');

if(ratingForm){
document.getElementById('ratingForm').addEventListener('submit', function(event) {
  event.preventDefault(); // Prevent the form from submitting normally

  debugger;
  // Get the checked value of the radio buttons
  var ratingValue = document.querySelector('input[name="rating"]:checked').value;

  // Set the rating value in the input field with ID "ratingInput"
  document.getElementById('ratingInput').value = ratingValue;
  var review = document.getElementById('review_text').value;
  var shipment_id = document.getElementById('id_shipment').value;
  var carrier_request_id = document.getElementById('carrier_request_id').value;
  var review_id = document.getElementById('review_id').value;
  var rating_id = document.getElementById('rating_id').value;

  var formData = {'rating' : ratingValue, 'review' : review , 'shipment_id' : shipment_id,
  'carrier_request_id' : carrier_request_id,
  'review_id':review_id, 'rating_id' : rating_id
  }

  $.ajax({
    type: 'POST',
    url: '/shipper/submit_review/', // Replace 'your-endpoint-url' with your actual endpoint URL
    data: formData,
    success: function(response) {
      // Handle the success response here
      console.log(response);
      showAlert(response.msg);

      // You can perform further actions based on the response, such as displaying a success message or redirecting the user
    },
    error: function(xhr, errmsg, err) {
      // Handle any errors that occur during the AJAX request
      console.log(xhr.status + ": " + xhr.responseText);
    }
  });
});
}


function showAlert(message) {

    var alertMessage = document.getElementById('success_message');
    if (alertMessage) {
        alertMessage.textContent = message;
        alertMessage.style.display = 'block'; // Show the alert message
        setTimeout(function() {
            alertMessage.style.display = 'none'; // Hide the alert message after 5 seconds
        }, 5000); // 5000 milliseconds = 5 seconds
    }
}

if(document.getElementById('ratingInput')){
setRating(document.getElementById('ratingInput').value)
}

function setRating(ratingValue)
{

     ratingValue = parseInt(ratingValue)
     $('input[name="rating"][value="' + ratingValue + '"]').prop('checked', true);
}


var start_trip_id= document.getElementById('start_trip');

if(start_trip_id)
{
document.getElementById('start_trip').addEventListener('click', function(event) {

    update_trip_status(0, null)
    document.getElementById('id_btn_update_location').disabled = false;
  });
}
/*if(document.getElementById('current_lat'))
{
calculateTimeBetweenPoints();
}*/

function calculateTimeBetweenPoints() {
debugger;
    var pickupLocationInput = document.getElementById('pickup_location');
    var dropOffLocationInput = document.getElementById('drop_off_location');
    var current_lat = document.getElementById('current_lat');
    var current_lng = document.getElementById('current_lng');

    // Check if inputs exist and have values
    if (pickupLocationInput && dropOffLocationInput && pickupLocationInput.value && dropOffLocationInput.value) {
        var pickupLocation = pickupLocationInput.value.split(',');
        var dropOffLocation = dropOffLocationInput.value.split(',');

        // Convert coordinates to numbers
        var pointA = { lat: parseFloat(pickupLocation[0]), lng: parseFloat(pickupLocation[1]) };
        var pointB = { lat: parseFloat(dropOffLocation[0]), lng: parseFloat(dropOffLocation[1]) };
        var current_location = { lat: parseFloat(current_lat.value), lng: parseFloat(current_lng.value) };

    var directionsService = new google.maps.DirectionsService();

    var request = {
        origin: current_location,
        destination: pointA,
        travelMode: 'DRIVING' // You can change the travel mode as needed
    };

    directionsService.route(request, function(response, status) {
        if (status == 'OK') {
            var route = response.routes[0];
            var leg = route.legs[0];
            var duration = leg.duration.text; // Duration in a human-readable format

            console.log('Duration:', duration);
            // You can use the duration for further processing or display to the user
        } else {
            console.error('Error:', status);
            // Handle errors if the directions service request fails
        }
    });
    }
}

function update_current_location()
{
    debugger;
    const checkboxes = document.querySelectorAll('input[type="checkbox"][name="mark_as_done"]');

    // Initialize an empty array to store checked checkbox IDs
    const checkedCheckboxIds = [];

    // Loop through all checkboxes
    checkboxes.forEach(checkbox => {
        // If the checkbox is checked, add its ID to the array
        if (checkbox.checked) {
            checkedCheckboxIds.push(checkbox.id);
        }
    });

    // Get the last ID from the array
    var lastCheckedId = checkedCheckboxIds.length > 0 ? checkedCheckboxIds[checkedCheckboxIds.length - 1] : null;

    // Output the last checked checkbox ID (just for demonstration)
    console.log("Last Checked Checkbox ID:");
    console.log(lastCheckedId);

    if (lastCheckedId == null)
        lastCheckedId = 1

    var current_location = (document.getElementById('id_current_location').value)

    update_trip_status(lastCheckedId-1, current_location)
    document.getElementById('id_current_address').value = ''
    document.getElementById('id_current_city').value = ''
    document.getElementById('id_current_location').value = ''


}


function onClickMarkAsDone(checkbox)
{
var clickedId = checkbox.id;
if(clickedId ==1 )
{
return;
}

    // Loop through checkboxes
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(function(cb) {
        // Check if the current checkbox is before the clicked checkbox
        if (cb.id < clickedId) {
            cb.checked = true;  // Mark the checkbox as checked
            cb.disabled = true;  // Mark the checkbox as checked
        }
    });

    update_trip_status(parseInt(clickedId)-1, null)



}

function update_trip_status(current_point, current_location)
{
    var plan_id = document.getElementById('plan_id').value
debugger;

var formData = {'plan_id' : plan_id, 'current_point' : current_point, 'current_location' : current_location}
$.ajax({
    type: 'POST',
    url: '/carrier/update_trip_status/', // Replace 'your-endpoint-url' with your actual endpoint URL
    data: formData,
    success: function(response) {
      // Handle the success response here
      debugger;
      if(response != null)
      {
        for(var i = 0; i< response.tracking_time_list.length ; i++ )
        {
            var id= response.tracking_time_list[i].index;
            document.getElementById('lat_'+id).value = response.tracking_time_list[i].waypoint.lat
            document.getElementById('lng_'+id).value = response.tracking_time_list[i].waypoint.lng
            }
             for(var i = 0; i< response.path_seq.length ; i++ ){
             var id= i+1;
            document.getElementById('time_'+id).innerHTML = response.path_seq[i].time
            document.getElementById('date_'+id).innerHTML = response.path_seq[i].date
            document.getElementById('status_'+id).innerHTML = response.path_seq[i].status
        }
      }


      console.log(response);

      // You can perform further actions based on the response, such as displaying a success message or redirecting the user
    },
    error: function(xhr, errmsg, err) {
      // Handle any errors that occur during the AJAX request
      console.log(xhr.status + ": " + xhr.responseText);
    }
  });
}


function view_carrier_profile(carrier_id)
{
var formData = {'carrier_id' : carrier_id}
$.ajax({
    type: 'POST',
    url: '/shipper/view_carrier_profile/', // Replace 'your-endpoint-url' with your actual endpoint URL
    data: formData,
    success: function(response) {
      debugger;

                $("#modalContent").html(response);
                $("#myModal").modal();
    },
    error: function(xhr, errmsg, err) {
      console.log(xhr.status + ": " + xhr.responseText);
    }
  });
  }