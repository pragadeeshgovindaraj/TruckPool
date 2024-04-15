import io
import json
import math
import os
from datetime import datetime, timedelta

import qrcode
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Avg

from django.shortcuts import render, redirect, get_object_or_404

import base64

from django.views.decorators.csrf import csrf_exempt
import requests
from users.decorators import carrier_required

from .forms import CarrierPlanForm
from .models import CarrierPlan, CarrierPlanRoute, CarrierCurrentLocation
from users.models import Carrier

from shipper.models import Shipment

from django.shortcuts import render
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  # Install xhtml2pdf: pip install xhtml2pdf
from PIL import Image

from shipper.models import CarrierRequest, Rating

from users.views import get_carrier_alerts

from shipper.views import load_truck, retrieve_rating_carrier, retrieve_carrier_reviews

import googlemaps

from shipper.models import ShipmentRequestTracking


apikey = "AIzaSyCWaQEjD36vYF2wHyocZl0DrkSkXBvTCvc"


# Create your views here.

def chatbot_window(request):
    list_of_ques = ["What do I do if my package shows as delivered, but it's not here?",
                    "Do you offer international shipping?", " Can I set a specific time for my delivery?",
                    " Do you offer expedited shipping options?", "What is the process of shipping through Truckpool?"]

    return render(request, 'carrier/chatbot_window.html', {'questions': list_of_ques})


@carrier_required
@login_required
def carrier_plans(request):
    user = request.user
    try:
        carrier_instance = get_object_or_404(Carrier, user_id=request.user.id)
    except:
        message = "Carrier User ID is invalid";
    # Retrieve all plans for the user
    user_plans = CarrierPlan.objects.filter(carrier_user=carrier_instance).order_by('-id')
    num_plans = len(user_plans)

    for plan in user_plans:
        message = None
        pending_shipments = (CarrierRequest.objects
                             .filter(carrier_plan_id=plan.id,
                                     status='pending')
                             .values_list('shipment_id', flat=True))
        unpaid_shipments = (CarrierRequest.objects
                            .filter(carrier_plan_id=plan.id,
                                    status='accepted')
                            .values_list('shipment_id', flat=True))
        no_of_pending_requests = len(pending_shipments)
        no_of_unpaid_requests = len(unpaid_shipments)

        if no_of_pending_requests > 0 or no_of_unpaid_requests > 0:
            message_pending = f'{no_of_pending_requests} pending requests'
            message_unpaid = f'{no_of_unpaid_requests} un-paid requests'
            message = f'You have {message_pending},  {message_unpaid}  for this plan.'
        plan.message = message

    carrier_alerts = get_carrier_alerts(request)
    num_requests = len(carrier_alerts)

    return render(request, "carrier/carrier_plans.html",
                  {'carrier_plans': user_plans, 'num_plans': num_plans, 'carrier_requests': carrier_alerts
                      , 'num_requests': num_requests, 'menu_item_plan': 'active'})


@carrier_required
@login_required
def carrier_shipments_requests(request, plan_id):
    user = request.user
    try:
        carrier_instance = get_object_or_404(Carrier, user_id=request.user.id)
    except:
        carrier_instance = None
        message = "Carrier User ID is invalid"

    # Retrieve all request received for the user
    if carrier_instance:
        if plan_id == 0:
            carrier_requests_all = CarrierRequest.objects.filter(carrier_id=carrier_instance.id).order_by('-id')
        else:
            carrier_requests_all = CarrierRequest.objects.filter(carrier_id=carrier_instance.id,
                                                                 carrier_plan_id=plan_id).order_by('-id')
        carrier_requests = CarrierRequest.objects.filter(carrier_id=carrier_instance.id, status='pending')
        num_requests = len(carrier_requests)
        num_requests_all = len(carrier_requests_all)
    else:
        carrier_requests_all = None
        num_requests_all = None
        carrier_requests = None
        num_requests = None

    return render(request, "carrier/carrier_shipments_requests.html",
                  {'carrier_requests': carrier_requests, 'carrier_requests_all': carrier_requests_all,
                   'num_requests': num_requests,
                   'num_requests_all': num_requests_all,
                   'menu_item_shipment': 'shipment'})


@carrier_required
@login_required
def make_plan(request):
    global carrier_instance
    carrier_instance = get_object_or_404(Carrier, user_id=request.user.id)
    if request.method == 'POST':
        form = CarrierPlanForm(request.POST, user=request.user)
        if form.is_valid():
            # Save the form data to create a new CarrierPlan instance
            carrier_plan = form.save(commit=False)
            try:
                carrier_instance = get_object_or_404(Carrier, user_id=request.user.id)
            except:
                form.add_error("Carrier User ID is invalid");

            carrier_plan.carrier_user = carrier_instance  # Assign the current user to the carrier plan
            carrier_plan.save()
            return redirect('carrier_plans')  # Redirect to a success page or another view
    else:
        form = CarrierPlanForm(request.POST or None, user=request.user)

    carrier_alerts = get_carrier_alerts(request)
    num_requests = len(carrier_alerts)

    return render(request, 'carrier/make_plan.html',
                  {'form': form, 'carrier_instance': carrier_instance, 'carrier_requests': carrier_alerts
                      , 'num_requests': num_requests})


@login_required
@carrier_required
def carrier_shipment_details(request, request_id):
    carrier_instance = get_object_or_404(Carrier, user_id=request.user.id)
    carrier_request = CarrierRequest.objects.get(pk=request_id)
    shipment_id = carrier_request.shipment_id

    try:
        shipment = get_object_or_404(Shipment, pk=shipment_id)
    except:
        shipment = None

    carrier_alerts = get_carrier_alerts(request)
    num_requests = len(carrier_alerts)

    return render(request, "carrier/carrier_shipment_details.html",
                  {'form': None, 'shipment': shipment, 'carrier_requests': carrier_alerts
                      , 'num_requests': num_requests, 'menu_item_shipment': 'active',
                   'carrier_request': carrier_request, 'request_id': request_id
                   })


@login_required
@carrier_required
def shipment_accept(request, request_id):
    carrier_request = CarrierRequest.objects.get(pk=request_id)
    shipment_id = carrier_request.shipment_id

    try:
        shipment = get_object_or_404(Shipment, pk=shipment_id)
    except:
        shipment = None

    carrier_request.status = 'accepted'
    carrier_request.save()

    shipment.status = 'payment Pending'
    shipment.save()

    carrier_alerts = get_carrier_alerts(request)
    num_requests = len(carrier_alerts)

    return render(request, "carrier/carrier_shipment_details.html",
                  {'form': None, 'shipment': shipment, 'carrier_requests': carrier_alerts
                      , 'num_requests': num_requests, 'menu_item_shipment': 'active', 'request_id': request_id
                   })



@login_required
@carrier_required
def shipment_reject(request, request_id):
    carrier_request = CarrierRequest.objects.get(pk=request_id)
    shipment_id = carrier_request.shipment_id

    try:
        shipment = get_object_or_404(Shipment, pk=shipment_id)
    except:
        shipment = None

    carrier_request.status = 'rejected'
    carrier_request.save()

    shipment.status = 'pending'
    shipment.save()

    carrier_alerts = get_carrier_alerts(request)
    num_requests = len(carrier_alerts)

    return render(request, "carrier/carrier_shipments_requests.html",
                  {'form': None, 'shipment': shipment, 'carrier_requests': carrier_alerts
                      , 'num_requests': num_requests, 'menu_item_shipment': 'active', 'request_id': request_id
                   })

def label_document(request, shipment_id):
    # Replace placeholders with actual data

    logo_path = settings.STATICFILES_DIRS[0] + '/images/logo.png'
    shipment = Shipment.objects.get(pk=shipment_id)

    qrcode_path = generate_qr_code(shipment_id)
    path = qrcode_path[qrcode_path.find("images"):]
    qrcode_path = settings.STATICFILES_DIRS[0] + '/' + path

    template = get_template('carrier/label_document.html')
    context = {
        'shipment': shipment,
        'logo_path': logo_path,
        'qrcode_path': qrcode_path
    }
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="shipment_label_{shipment_id}.pdf"'

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    if pisa_status.err:
        return HttpResponse('Error generating PDF')

    return response


def label_document_view(request, shipment_id):
    try:
        shipment = get_object_or_404(Shipment, pk=shipment_id)
    except:
        shipment = None
    return render(request, "carrier/label_document.html", {'shipment': shipment})


def link_callback(uri, rel):
    """
        Convert HTML URIs to absolute system paths so xhtml2pdf can access those
        resources
        """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri
    # make sure that file exists
    if not os.path.isfile(path):
        raise RuntimeError(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def generate_qr_code(shipment_id):
    # Get the shipment object
    shipment = get_object_or_404(Shipment, pk=shipment_id)

    # Generate the QR code content
    qr_content = f'Shipment ID: {shipment.id}\nShipper: {shipment.shipper_user.first_name} {shipment.shipper_user.last_name}\n' \
                 f'Pickup Location: {shipment.pickup_address}\nDrop-off Location: {shipment.drop_off_address}'

    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=2,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)

    # Create an image from the QR code
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code image to a BytesIO buffer
    qr_image_io = BytesIO()
    qr_image.save(qr_image_io, format='PNG')

    # Create a PIL Image object from the BytesIO buffer
    qr_pil_image = Image.open(qr_image_io)

    qr_pil_image.resize((300, 300))

    # Save the PIL Image to a file
    # qr_image_path = f'qr_code_{shipment_id}.png'
    # qr_pil_image.save(qr_image_path)

    # Save the QR code image to the model instance
    shipment.qrcode_image.save(f'qr_code_{shipment_id}.png', ContentFile(qr_image_io.getvalue()))
    return shipment.qrcode_image.url


@login_required
@carrier_required
@csrf_exempt
def shipment_truck_view(request, request_id):
    request_carrier = CarrierRequest.objects.get(pk=request_id)
    shipment = request_carrier.shipment
    carrier = request_carrier.carrier
    plan = request_carrier.carrier_plan
    vehicle = carrier.vehicle_type

    fig, packer = load_truck(shipment, plan, carrier, vehicle, True)
    # fig.show(block=True)
    # fig.close(0)

    buffer = BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)

    image_data = base64.b64encode(buffer.getvalue()).decode()

    context = {'image_data': image_data, 'request_id': request_carrier.id}
    return render(request, 'carrier/shipment_truck_view.html', context)


def generate_route(request, plan_id, criteria):
    message = None
    optimal_path = []
    optimal_sequence = []
    plan = CarrierPlan.objects.get(pk=plan_id)

    try:
        carrier_plan_route = CarrierPlanRoute.objects.get(carrier_plan_id=plan_id)
    except:
        carrier_plan_route = None

    if carrier_plan_route:
        route_json = carrier_plan_route.path_data
        route_json_json = json.dumps(route_json)
        path_sequence = carrier_plan_route.path_seq
    else:
        active_shipment_ids_current_plan = (CarrierRequest.objects
                                            .filter(carrier_plan_id=plan.id,
                                                    status='paid')
                                            .values_list('shipment_id', flat=True))

        active_shipments = Shipment.objects.filter(id__in=active_shipment_ids_current_plan)

        coordinates = {}
        # adding initial starting point of plan
        coordinates[(str(plan.id) + "~" + "start")] = {'address': plan.start_address,
                                                       'coordinates': plan.start_location}

        # adding all pickup points of shippers
        for shipment in active_shipments:
            coordinates[(str(shipment.id) + "~" + "pickup")] = {'address': shipment.pickup_address,
                                                                'coordinates': shipment.pickup_location}

        # adding all dropoff points of shippers
        for shipment in active_shipments:
            coordinates[(str(shipment.id) + "~" + "drop_off")] = {'address': shipment.drop_off_address,
                                                                  'coordinates': shipment.drop_off_location}

        # adding end point of plan
        coordinates[(str(plan.id) + "~" + "plan-end")] = {'address': plan.end_address, 'coordinates': plan.end_location}

        gmaps = googlemaps.Client(key=apikey)
        locations = list(coordinates.keys())
        matrix = [[0.0 for _ in range(len(locations))] for _ in range(len(locations))]
        optim_method = criteria
        if (optim_method == 'distance'):
            for i in range(len(locations)):
                for j in range(len(locations)):
                    if i != j:
                        origin = coordinates[locations[i]]['coordinates']
                        destination = coordinates[locations[j]]['coordinates']

                        # Make the distance matrix API request
                        result = gmaps.distance_matrix(
                            origins=origin,
                            destinations=destination,
                            mode='driving',
                            departure_time='now',
                            traffic_model='best_guess',
                        )

                        # Extract the distance in meters
                        distance_meter = result['rows'][0]['elements'][0]['distance']['value']
                        matrix[i][j] = distance_meter

            # Nearest Neighbor Algorithm
            def nearest_neighbor(matrix, start):
                n = len(matrix)
                unvisited = set(range(n))
                path = [start]
                leg_distances_meter = []
                current = start

                unvisited.remove(start)
                while unvisited:
                    nearest = min(unvisited, key=lambda x: matrix[current][x])
                    path.append(nearest)
                    leg_distances_meter.append(matrix[current][nearest])
                    unvisited.remove(nearest)
                    current = nearest

                return path, leg_distances_meter

            # Use the nearest neighbor algorithm starting from location Downtown Montreal (A)
            start_point = (str(plan.id) + "~" + "start")
            start_index = locations.index(start_point)
            optimal_path, leg_distances_meter = nearest_neighbor(matrix, start_index)

            # Convert indices to locations
            optimal_sequence = [locations[i] for i in optimal_path]

            # Output optimal sequence, total duration, and total distance
            print("Optimal Sequence:")
            print(optimal_sequence)

            total_distance_meter = sum(leg_distances_meter)
            total_distance_km = total_distance_meter / 1000
            print("\nTotal Road Distance Traveled:")
            print(f"{total_distance_km:.2f} kilometers ({total_distance_meter:.2f} meters)")
        elif (optim_method == 'time'):
            for i in range(len(locations)):
                for j in range(len(locations)):
                    if i != j:
                        origin = coordinates[locations[i]]['coordinates']
                        destination = coordinates[locations[j]]['coordinates']

                        # Make the distance matrix API request
                        result = gmaps.distance_matrix(
                            origins=origin,
                            destinations=destination,
                            mode='driving',
                            departure_time='now',
                            traffic_model='best_guess',
                        )

                        # Extract the duration in seconds
                        duration_sec = result['rows'][0]['elements'][0]['duration']['value']
                        matrix[i][j] = duration_sec

            # Nearest Neighbor Algorithm
            def nearest_neighbor(matrix, start):
                n = len(matrix)
                unvisited = set(range(n))
                path = [start]
                leg_durations_sec = []
                current = start

                unvisited.remove(start)
                while unvisited:
                    nearest = min(unvisited, key=lambda x: matrix[current][x])
                    path.append(nearest)
                    leg_durations_sec.append(matrix[current][nearest])
                    unvisited.remove(nearest)
                    current = nearest

                return path, leg_durations_sec

            # Use the nearest neighbor algorithm starting from location Downtown Montreal (A)
            start_point = (str(plan.id) + "~" + "start")
            start_index = locations.index(start_point)
            optimal_path, leg_durations_sec = nearest_neighbor(matrix, start_index)

            # Convert indices to locations
            optimal_sequence = [locations[i] for i in optimal_path]

            # Output optimal sequence and total duration
            print("Optimal Sequence:")
            print(optimal_sequence)

            total_duration_sec = sum(leg_durations_sec)
            total_duration_min = total_duration_sec / 60
            print("\nTotal Duration Traveled:")
            print(f"{total_duration_min:.2f} minutes ({total_duration_sec:.2f} seconds)")
        else:
            print(f'optim_method:{optim_method} not defined or improperly defined')

        coord = []

        for i in locations:
            cord = coordinates[i]['coordinates'].split(',')
            json_m = {
                "lat": float(cord[0]),
                "lng": float(cord[1])
            }
            coord.append(json_m)
        # print(coord)

        optimal_sequence_coord = [coord[i] for i in optimal_path]
        print(optimal_sequence_coord)

        route_json = {
            "waypoints": optimal_sequence_coord
        }

        path_sequence = []

        for path in optimal_sequence:
            p = path.split('~')
            path_json = {'id': p[0],
                         'pickup': True if p[1] == 'pickup' else False,
                         'start': True if p[1] == 'start' else False,
                         'end': True if p[1] == 'plan-end' else False,
                         'address': coordinates[path]['address']}
            path_sequence.append(path_json)

        route_json_json = json.dumps(route_json)

        # Create new entry after deleting old entries
        with transaction.atomic():
            # Delete entries older than the delete_date
            CarrierPlanRoute.objects.filter(carrier_plan_id=plan_id).delete()
            CarrierPlanRoute.objects.create(carrier_plan=plan, path_data=route_json, path_seq=path_sequence)

    plan_started = path_sequence[0].get('status') == 'Started'
    plan.status = 'Route Finalized'
    plan.save()

    return render(request, 'carrier/route_view.html',
                  {'carrier_plan': plan, 'route_json': route_json_json, 'path_sequence': path_sequence,
                   'plan_started': plan_started
                   })


@login_required
def carrier_profile(request):
    try:
        carrier_instance = get_object_or_404(Carrier, user_id=request.user.id)
        rating = retrieve_rating_carrier(carrier_instance)
        review = retrieve_carrier_reviews(carrier_instance)
    except:
        carrier_instance = None

    return render(request, 'carrier/carrier_profile.html',
                  {'carrier': carrier_instance,
                   'rating': rating, 'reviews': review})


def update_previous_points(route_info, current_point):
    for index, waypoint in enumerate(route_info.path_data['waypoints'][:current_point + 1]):
        path_seq = route_info.path_seq[index]
        shipment_track = None
        try:
            shipment = Shipment.objects.get(id=path_seq['id'])
        except:
            shipment = None

        if shipment:
            try:
                shipment_track = ShipmentRequestTracking.objects.get(shipment=shipment)
            except:
                shipment_track = None

        path_seq['time'] = ''
        path_seq['date'] = ''
        if path_seq['pickup']:
            if shipment_track:
                shipment_track.current_status = 'Picked'
                shipment_track.save()
            path_seq['status'] = 'Picked'
        elif path_seq['start']:
            path_seq['status'] = 'Started'
        elif path_seq['end']:
            path_seq['status'] = ''
        else:
            if shipment_track:
                shipment_track.current_status = 'Delivered'
                shipment_track.save()
            if shipment:
                try:
                    shipment_req = CarrierRequest.objects.filter(shipment=shipment).exclude(status='rejected').order_by('-id').first()
                    shipment_req.status = 'fulfilled'
                    shipment_req.save()
                    shipment.status = 'completed'
                    shipment.save()
                except:
                    shipment_req = None

            path_seq['status'] = 'Delivered'

        route_info.path_seq[index] = path_seq
        route_info.save()


@csrf_exempt
def update_trip_status(request):
    print(request)
    current_location = None
    plan_id = request.POST.get('plan_id')
    plan = CarrierPlan.objects.get(id=plan_id)
    current_point = int(request.POST.get('current_point'))
    current_location_from_client = request.POST.get('current_location')

    current_location_arr = []
    if current_location_from_client:
        current_location_arr = current_location_from_client.split(',')
        current_location = {'lat': float(current_location_arr[0]), 'lng': float(current_location_arr[1])}
        print(current_location_arr)

    try:
        route_info = CarrierPlanRoute.objects.get(carrier_plan=plan)
    except:
        route_info = None

    if current_location:
        start_point = current_location
    else:
        start_point = route_info.path_data['waypoints'][current_point]

    with transaction.atomic():
        CarrierCurrentLocation.objects.filter(carrier_plan=plan).delete()
        CarrierCurrentLocation.objects.create(carrier_plan=plan, latitude=start_point['lat'],
                                              longitude=start_point['lng'])

    new_time = datetime.now()
    tracking_time_list = []
    for index, waypoint in enumerate(route_info.path_data['waypoints'][current_point:]):
        index_in = index + current_point
        if index == 0:
            if not current_location:
                current_location = waypoint
            path_seq = route_info.path_seq[index_in]
            tracking_time = {'index': index_in + 1, 'waypoint': waypoint, 'distance_km': '',
                             'travel_time_minutes': '', 'time': new_time.time().strftime("%H:%M"),
                             'date': new_time.date()}
            tracking_time_list.append(tracking_time)
            path_seq['time'] = new_time.time().strftime("%H:%M")
            path_seq['date'] = new_time.date().isoformat()
            path_seq['status'] = ''
            update_previous_points(route_info, current_point)
        else:
            path_seq = route_info.path_seq[index_in]

            # Calculate distance between Montreal and Toronto
            distance_km = calculate_distance(current_location['lat'], current_location['lng'], waypoint['lat'],
                                             waypoint['lng'])

            # Assume average speed in kilometers per hour (e.g., 100 km/h)
            average_speed_kmph = 60
            loading_time = 10

            # Calculate travel time
            travel_time_minutes = calculate_travel_time(distance_km, average_speed_kmph)
            travel_time_minutes = travel_time_minutes + loading_time

            new_time = new_time + timedelta(minutes=travel_time_minutes)

            print(f"Distance: {distance_km:.2f} kilometers")
            print(f"Travel Time: {travel_time_minutes:.2f} miuntes")

            tracking_time = {'index': index_in + 1, 'waypoint': waypoint, 'distance_km': distance_km,
                             'travel_time_minutes': travel_time_minutes, 'time': new_time.time().strftime("%H:%M"),
                             'date': new_time.date()}
            tracking_time_list.append(tracking_time)
            path_seq['time'] = new_time.time().strftime("%H:%M")
            path_seq['date'] = new_time.date().isoformat()
            path_seq['status'] = ''
            update_previous_points(route_info, current_point)

            route_info.path_seq[index_in] = path_seq
            route_info.save()

            try:
                shipment = Shipment.objects.get(id=path_seq['id'])

            except:
                shipment = None

            if shipment:
                try:
                    shipment_tracking = ShipmentRequestTracking.objects.get(shipment=shipment)
                except:
                    shipment_tracking = None

                if shipment_tracking:
                    if path_seq['pickup']:
                        shipment_tracking.est_pickup_time = new_time
                    else:
                        shipment_tracking.est_drop_off_date = new_time
                    shipment_tracking.save()
                else:
                    if path_seq['pickup']:
                        ShipmentRequestTracking.objects.create(carrier_plan=plan, shipment=shipment, current_status='',
                                                               est_pickup_time=new_time)
                    else:
                        ShipmentRequestTracking.objects.create(carrier_plan=plan, shipment=shipment, current_status='',
                                                               est_drop_off_date=new_time)

    return JsonResponse(
        {'value': 'new Data', 'tracking_time_list': tracking_time_list, 'path_seq': route_info.path_seq})


def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    radius = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Calculate the differences in latitude and longitude
    d_lat = lat2_rad - lat1_rad
    d_lon = lon2_rad - lon1_rad

    # Haversine formula to calculate distance
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c

    return distance


def calculate_travel_time(distance, average_speed):
    # Calculate travel time in hours
    travel_time_minutes = distance / average_speed
    return travel_time_minutes * 60
