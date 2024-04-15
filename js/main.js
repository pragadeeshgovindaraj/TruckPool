

var current_fs, next_fs, previous_fs; //fieldsets
var opacity;

$(".next").click(function(){

    current_fs = $(this).parent();
    next_fs = $(this).parent().next();

    //Add Class Active
    $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");

    //show the next fieldset
    next_fs.show();
    //hide the current fieldset with style
    current_fs.animate({opacity: 0}, {
        step: function(now) {
            // for making fielset appear animation
            opacity = 1 - now;

            current_fs.css({
                'display': 'none',
                'position': 'relative'
            });
            next_fs.css({'opacity': opacity});
        },
        duration: 600
    });
});

$(".previous").click(function(){

    current_fs = $(this).parent();
    previous_fs = $(this).parent().prev();

    //Remove class active
    $("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");

    //show the previous fieldset
    previous_fs.show();

    //hide the current fieldset with style
    current_fs.animate({opacity: 0}, {
        step: function(now) {
            // for making fielset appear animation
            opacity = 1 - now;

            current_fs.css({
                'display': 'none',
                'position': 'relative'
            });
            previous_fs.css({'opacity': opacity});
        },
        duration: 600
    });
});

$('.radio-group .radio').click(function(){
    $(this).parent().find('.radio').removeClass('selected');
    $(this).addClass('selected');
});

$(".submit").click(function(){
    return false;
})


    function initMap() {
        // Set the default location (e.g., a city or a specific address)

        var defaultLocation = { lat: 37.7749, lng: -122.4194 };

        // Create the map
        var map = new google.maps.Map(document.getElementById('map'), {
            center: defaultLocation,
            zoom: 12
        });

        // Create a marker for the default location
        var marker = new google.maps.Marker({
            position: defaultLocation,
            map: map,
            draggable: true // Allow the marker to be draggable
        });

        // Listen for the marker's dragend event to get the updated location
        google.maps.event.addListener(marker, 'dragend', function (event) {
            var updatedLocation = {
                lat: event.latLng.lat(),
                lng: event.latLng.lng()
            };

            // Log the updated location (you can use this data as needed)
            console.log('Updated Location:', updatedLocation);
        });

        // Listen for the map's click event to get the clicked location
        google.maps.event.addListener(map, 'click', function (event) {
            var clickedLocation = {
                lat: event.latLng.lat(),
                lng: event.latLng.lng()
            };

            // Log the clicked location (you can use this data as needed)

            console.log('Clicked Location:', clickedLocation);
            $('#BaseAutoComplete_withValidationMessage-59').val(clickedLocation.lat)
            // Update the marker position
            marker.setPosition(clickedLocation);
        });
    }

 function initMapOnClick(field_id, latlong_id, city_field_id) {
        var defaultLocation = { lat: 45.513743, lng: -73.583090 };
        var map = new google.maps.Map(document.getElementById('map'), {
            center: defaultLocation,
            zoom: 12
        });

        var marker = new google.maps.Marker({
            position: defaultLocation,
            map: map,
            draggable: true
        });

        google.maps.event.addListener(marker, 'dragend', function (event) {
            var updatedLocation = {
                lat: event.latLng.lat(),
                lng: event.latLng.lng()
            };
            document.getElementById('locationInput').value = updatedLocation.lat + ', ' + updatedLocation.lng;
        });

        google.maps.event.addListener(map, 'click', function (event) {
            var clickedLocation = {
                lat: event.latLng.lat(),
                lng: event.latLng.lng()
            };

             $('#'+latlong_id).val(clickedLocation.lat + ', ' + clickedLocation.lng);
             getLocationName(clickedLocation.lat , clickedLocation.lng, field_id, city_field_id);


             marker.setPosition(clickedLocation);
            closeMapModal()
        });
    }


 function loadMapScript() {
        var script = document.createElement('script');
        script.type = 'text/javascript';
        //script.src = 'https://maps.googleapis.com/maps/api/js?key=AIzaSyCk_5pj5OJufDsnZIx4YRHqlpz9fblcQ5o&libraries=places&callback=initMap';
        script.src = 'https://maps.googleapis.com/maps/api/js?key=AIzaSyCWaQEjD36vYF2wHyocZl0DrkSkXBvTCvc&libraries=places&callback=initMap';
        document.body.appendChild(script);
    }
if(document.getElementById('map')){

    // Load the map script when the page is loaded
    window.onload = loadMapScript;
    }

  function openMap(field, latlong_id, city_field_id) {
        document.getElementById('mapModal').style.display = 'flex';
        initMapOnClick(field.id, latlong_id, city_field_id); // Initialize the map when the modal is opened
    }

    // Close the map modal
    function closeMapModal() {
        document.getElementById('mapModal').style.display = 'none';
    }

function updateOverlayText(obj, objshow_id) {
        // Get the selected value from the dropdown
        var selectedValue = obj.value;

        // Update the content of the span with the selected value
        document.getElementById(objshow_id).textContent = selectedValue;
    }

  function getLocationName(latitude, longitude, field_id, city_field_id) {
    const geocoder = new google.maps.Geocoder();
    const latLng = new google.maps.LatLng(latitude, longitude);

    geocoder.geocode({ location: latLng }, (results, status) => {
      if (status === 'OK') {
        if (results[0]) {

          const locationName = results[0].formatted_address;
const city = getCityFromGeocoding(results);
console.log("City:", city);
           $('#'+field_id).val(locationName);
           $('#'+city_field_id).val(city);
          console.log('Location Name:', locationName);
        } else {
          console.error('No results found');
        }
      } else {
        console.error('Geocoder failed due to:', status);
      }
    });
  }

  function getCityFromGeocoding(response) {
  debugger;
  const result = response[0];

  if (result) {
    const cityComponent = result.address_components.find(
      (component) => component.types.includes("locality")
    );

    if (cityComponent) {
      return cityComponent.long_name;
    }
  }

  return null;
}


function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Radius of the Earth in kilometers
  const dLat = (lat2 - lat1) * (Math.PI / 180);
  const dLon = (lon2 - lon1) * (Math.PI / 180);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * (Math.PI / 180)) *
      Math.cos(lat2 * (Math.PI / 180)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  const distance = R * c; // Distance in kilometers
  return distance;
}






function get_estimate()
{
   if(!validateInputs())
   {
        debugger;
        document.getElementById('id_length').focus();
        showAlert('Package Size should not be less than  0.1(m) or 10(cm) or 4(in)');
        return;
   }

    var origin = ($('#id_pickup_location').val()).split(',');
    var length = ($('#id_length').val());
    var width = ($('#id_width').val());
    var height = ($('#id_height').val());
    var weight = ($('#id_weight').val());
    var quantity = ($('#id_quantity').val());
    var length_unit = ($('#id_unit_size').val());
    var weight_unit = ($('#id_unit_weight').val());
    var pick_up_date = ($('#id_pickup_date').val());
    var dest = ($('#id_drop_off_location').val()).split(',');
 $.ajax({
        url: '/shipper/generate_estimate/',  // Replace with the actual URL to your server endpoint
        method: 'POST',
        data: {length:length,
        width:width,
        height:height,
        weight: weight,
        quantity: quantity,
        length_unit: length_unit,
        weight_unit: weight_unit,
        pick_up_date: pick_up_date,
        origin:{lat: origin[0] ,long: origin[1]},
        destination:{lat: dest[0],long:dest[1]}},
        success: function(data) {
          // Update other fields based on the serialized product object.

          $("#id_estimated_quotation").val(data.value);

          // Add more fields as needed
        },
        error: function(error) {
          console.log('Error:', error);
        }

    });
}


function show_truck_load(){

request_id = document.getElementById('request_id').value;
debugger;
 document.getElementById('plotModal').style.display = 'flex';
/*
 $.ajax({
        url: '/carrier/shipment_truck_view/'+request_id+'/',  // Replace with the actual URL to your server endpoint
        method: 'GET',

         success: function(data) {
          // Update other fields based on the serialized product object.

          // Add more fields as needed
        },
        error: function(error) {
          console.log('Error:', error);
        }
        }
        );
*/


       }


function closePlotModal()
{ document.getElementById('plotModal').style.display = 'None';

}


function book_shipper(calculated_quote, carrier_id, shipment_id, plan_id){

        $.ajax({
        url: '/shipper/book_carrier/',  // Replace with the actual URL to your server endpoint
        method: 'POST',
        data: {'carrier_user_id' : carrier_id, 'shipment_id' : shipment_id, 'plan_id' : plan_id, 'calculated_quote': calculated_quote},
        success: function(data) {
          // Update other fields based on the serialized product object.

          $("#id_shipper_action_"+plan_id).html('Requested');
          $(".shipper_book").prop("disabled", true);
           $('#alert').removeClass('hidden'); //
           $('#message').html(data['book_message']); //



          // Add more fields as needed
        },
        error: function(error) {
          console.log('Error:', error);

        }

    });

}
let chatSocket;
if(document.getElementById('chatModal')) {
debugger;
        chatSocket = new WebSocket("ws://" + window.location.host + "/users/ws/chat/");
        chatSocket.onopen = function (e) {
            console.log("The connection was set up successfully!");
        };
        chatSocket.onclose = function (e) {
            console.log("Something unexpected happened!");
        };
        }

function openChat(receiver_username, sender_username)
{
     document.getElementById('chatModal').style.display = 'flex';
        document.getElementById('chatButton').style.display = 'none';
        document.querySelector("#id_message_send_input").focus();
        document.querySelector("#id_message_send_input").onkeyup = function (e) {
            if (e.keyCode == 13) {
                document.querySelector("#id_message_send_button").click();
            }
        };
        document.querySelector("#id_message_send_button").onclick = function (e) {
            var messageInput = document.querySelector("#id_message_send_input").value;
            var currentTime = new Date();
            var time = currentTime.toLocaleTimeString();
            chatSocket.send(JSON.stringify({
                message: messageInput,
                username: sender_username,
                time: time,
                receiver_user_id : receiver_username
            }));
        };
        chatSocket.onmessage = function (e) {
            const data = JSON.parse(e.data);
            var to_send_username = (document.getElementById('to_send_username').innerHTML).toLowerCase();
            var logged_in_user = (document.getElementById('logged_in_user').value).toLowerCase();
            if((data.msg_type == 'S' && data.username.toLowerCase() == logged_in_user && to_send_username == (data.receiver_user_id).toLowerCase())
                || (data.msg_type == 'R' && data.username.toLowerCase() == to_send_username &&  logged_in_user  == (data.receiver_user_id).toLowerCase())){
            var messageContainer = document.querySelector("#id_chat_item_container");
            var div = document.createElement("div");
            if(data.error === undefined){
            div.className = (data.username === sender_username) ? "chat-message right" : "chat-message left";
            div.innerHTML = `<div class="message-content">
                <span class="message-username">${data.username.charAt(0).toUpperCase() + data.username.slice(1)}</span>
                <span class="message-text" style="padding-right: 200px;">${data.message}</span>
                <span class="message-timestamp">${data.time}</span>
            </div>`;
            }else
            {
               div.className = "chat-message red";
            div.innerHTML = `<div class="message-content">
                <span class="message-text">${data.error}</span>
            </div>`;
            }
            document.querySelector("#id_message_send_input").value = "";
            messageContainer.appendChild(div);
            // Scroll to the bottom of the chat container
            messageContainer.scrollTop = messageContainer.scrollHeight;
            }
        };
}


 function closeChatModal() {
        document.getElementById('chatModal').style.display = 'none';
        document.getElementById('chatButton').style.display = 'flex';
    }

  function onChatBotSend_pre(obj) {
        onChatBotSend(obj.id)

  }
  function onChatBotSend(obj_id) {

            message =  document.getElementById(obj_id).value;

            //const data = JSON.parse(e.data);
            const data = {
                'username' : 'abc',
                'avatar-user' : 'user',
                'avatar-chat' : 'chatbot',
                'message' : message,
                'time' : (new Date().toISOString().slice(0, 19).replace('T', ' ')),
                'image_url' : '../static/images/user_profile.svg'

            }
            appendMessageChatBot(data);
             $.ajax({
        url: '/users/chat_with_bot/',  // Replace with the actual URL to your server endpoint
        method: 'POST',
        data: data,
         success: function(data) {
          // Update other fields based on the serialized product object.

           appendMessageChatBot(data);

          // Add more fields as needed
        },
        error: function(error) {
          console.log('Error:', error);
        }
        });

        };


function appendMessageChatBot(data)
{
 var messageInput = document.querySelector("#id_message_send_input-chatbot").value;
            var messageContainer = document.querySelector("#id_chat_item_container-chatbot");
            var div = document.createElement("div");
            if(data.error === undefined){
            //div.className = (data.username === sender_username) ? "chat" : "chat chat-left";
            div.className = (data.is_reply) ? "chat chat-left" : "chat";
            div.innerHTML = `
            <div class="chat-avatar" id="chat-avatar">
            <a class="avatar avatar-online" data-toggle="tooltip" href="#" data-placement="right" title="">
                     <img src="${data.image_url}" alt="...">
              <i></i>
            </a>
          </div>
           <div class="chat-body">
            <div class="chat-content">
              <p id="message">
                ${data.message}
              </p>
              <time class="chat-time" datetime="2015-07-01T11:37">${data.time}</time>
            </div>
          </div>`;
            }
            document.querySelector("#id_message_send_input-chatbot").value = "";
            messageContainer.appendChild(div);
            // Scroll to the bottom of the chat container
            messageContainer.scrollTop = messageContainer.scrollHeight;
}

document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            // Check if the event occurred inside a form input field
            if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') {
                // Prevent the default form submission
                event.preventDefault();
                // Trigger the click event on the button with the specified ID
                document.getElementById('id_message_send_button-chatbot').click();
            }
        }
    });
});

var book_shipment_form=document.querySelector("#book_shipment_button");

if(book_shipment_form!=undefined){

book_shipment_form.addEventListener('submit', function(event) {
    // Prevent the form from submitting

    event.preventDefault();

    // Your custom validation function
    if (validateInputs()) {
        // If validation passes, you can submit the form programmatically

        this.submit();
    } else {
        // Handle validation error, show messages, etc.
        document.getElementById('id_length').focus();
        showAlert('Package Size should not be less than  0.1(m) or 10(cm) or 4(in)');
        return;
    }
});
}

function validateInputs()
{
    var length = $('#id_length').val();
    var height = $('#id_height').val();
    var width = $('#id_width').val();

    var unit_of_dimension = $('#id_unit_size').val();

if (unit_of_dimension == 'in') {
    length *= 0.0254; // Convert inches to meters (1 inch = 0.0254 meters)
    height *= 0.0254;
    width *= 0.0254;
} else if (unit_of_dimension == 'cm') {
    length *= 0.01; // Convert centimeters to meters (1 cm = 0.01 meters)
    height *= 0.01;
    width *= 0.01;
}

if (length < 0.1 || width < 0.1 || height < 0.1)
{
    return false;
}

return true;
}


function showAlert(message) {

    var alertMessage = document.getElementById('error_message');
    if (alertMessage) {
        alertMessage.textContent = message;
        alertMessage.style.display = 'block'; // Show the alert message
        setTimeout(function() {
            alertMessage.style.display = 'none'; // Hide the alert message after 5 seconds
        }, 5000); // 5000 milliseconds = 5 seconds
    }
}


var space_available = document.getElementById('id_space_available');

if(space_available){
space_available.addEventListener('input', function(event) {
            var value = parseFloat(event.target.value);
            var max = parseFloat(event.target.max);
            var min = parseFloat(event.target.min);
             event.target.value = value
            if (value > max) {
                event.target.value = max; // Reset value to maximum if it exceeds max
            }
            if (value < min)
            {
              event.target.value = min;
              }
        });
        }

