import random
import uuid
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Subquery, OuterRef, Avg
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .forms import ShipmentForm, PaymentDetailsForm
from .models import Shipment, CarrierRequest, PaymentDetails, Rating, Review, ShipmentRequestTracking
import googlemaps

from users.models import ShipperIndividual

from users.decorators import shipper_required

from carrier.models import CarrierPlan

from users.models import Carrier

from users.views import get_carrier_alerts_accepted
from py3dbp import Packer, Bin, Item, Painter

from    carrier.models import CarrierCurrentLocation, CarrierPlanRoute


apikey = "AIzaSyCWaQEjD36vYF2wHyocZl0DrkSkXBvTCvc"


@login_required
@shipper_required
def book_shipment(request):
    message = ''
    operation = None
    return_redirect = None
    if request.method == 'POST':
        if 'edit_shipment' in request.POST:
            shipment_id = request.POST.get('shipment_id')
            shipment = Shipment.objects.get(id=shipment_id)
            form = ShipmentForm(request.POST, request.FILES, instance=shipment)
            operation = 'Updated'
        else:
            form = ShipmentForm(request.POST)
            operation = 'Saved'
            form.instance.status = 'pending'

        if form.is_valid():
            shipment_instance = form.save()
            shipment_id = shipment_instance.pk

            if request.POST.get('unit_size') == 'in':
                shipment_instance.length = inches_to_meters(float(request.POST.get('length')))
                shipment_instance.width = inches_to_meters(float(request.POST.get('width')))
                shipment_instance.height = inches_to_meters(float(request.POST.get('height')))
            elif request.POST.get('unit_size') == 'cm':
                shipment_instance.length = cm_to_meter(float(request.POST.get('length')))
                shipment_instance.width = cm_to_meter(float(request.POST.get('width')))
                shipment_instance.height = cm_to_meter(float(request.POST.get('height')))
            else:
                shipment_instance.length = (float(request.POST.get('length')))
                shipment_instance.width = (float(request.POST.get('width')))
                shipment_instance.height = (float(request.POST.get('height')))

            # shipment_weight calculation
            if request.POST.get('unit_weight') == 'lbs':
                shipment_instance.weight = lbs_to_kg(float(request.POST.get('weight')))
            else:
                shipment_instance.weight = float(request.POST.get('weight'))

            shipment_instance.save()
            # form.save()
            message = operation + " Successfully"
            # shipment_id = form.auto_id
            if 'edit_shipment' in request.POST:
                return_redirect = 'shipment_details/' + str(shipment_id) + '/Q'
            else:
                return_redirect = 'edit_shipment/' + str(shipment_id) + '/'
            return redirect(return_redirect)  # Redirect to a view displaying the list of shipments

    else:
        form = ShipmentForm()

    shipper_alerts = get_carrier_alerts_accepted(request)
    num_requests = len(shipper_alerts)

    return render(request, "shipper/book_shipment.html",
                  {'form': form, 'success_message': message, 'shipper_alerts': shipper_alerts,
                   'num_requests': num_requests, 'menu_item_book_shipment': 'active'})


@login_required
@shipper_required
def edit_shipment(request, shipment_id):
    shipment = get_object_or_404(Shipment, pk=shipment_id)

    if request.method == 'POST':
        form = ShipmentForm(request.POST, instance=shipment)
        if form.is_valid():
            form.save()
            # Handle successful form submission, e.g., redirect to a success page
    else:
        form = ShipmentForm(instance=shipment)

    shipper_alerts = get_carrier_alerts_accepted(request)
    num_requests = len(shipper_alerts)
    return render(request, 'shipper/book_shipment.html',
                  {'form': form, 'shipment': shipment, 'shipper_alerts': shipper_alerts, 'num_requests': num_requests})


@login_required
@shipper_required
def shipment_details(request, shipment_id, sort_by):
    try:
        shipment = get_object_or_404(Shipment, pk=shipment_id)
    except:
        shipment = None

    try:
        booked_plan = get_object_or_404(CarrierRequest.objects.exclude(status='rejected'), shipment_id=shipment_id)
    except:
        booked_plan = None

    carriers = match_with_carrier(request, shipment)

    for plan in carriers:
        plan.calculated_quote = generate_estimate_plan(shipment, plan.desired_rate, plan)
        plan.rating = retrieve_rating_carrier(plan.carrier_user)

    # sorting by rate
    if sort_by == 'Q':
        carriers = sorted(carriers, key=lambda x: x.calculated_quote)

    # sorting by rate
    if sort_by == 'R':
        carriers = sorted(carriers, key=lambda x: x.rating, reverse=True)

    shipper_alerts = get_carrier_alerts_accepted(request)
    num_requests = len(shipper_alerts)
    return render(request, "shipper/shipment_details.html",
                  {'form': None, 'shipment': shipment, 'carrier_plans': carriers, 'shipper_alerts': shipper_alerts,
                   'booked_plan': booked_plan,
                   'num_requests': num_requests}
                  )


@login_required
@shipper_required
def view_shipment_details(request, shipment_id):
    plan = None
    current_location = None
    try:
        shipment = get_object_or_404(Shipment, pk=shipment_id)
    except:
        shipment = None

    try:
        carrier_request = CarrierRequest.objects.filter(shipment_id=shipment_id,
                                                        status__in=['paid', 'fulfilled']).first()
        if carrier_request:
            try:
                payment_details = PaymentDetails.objects.filter(request_id=carrier_request.pk).first()
                plan = CarrierPlan.objects.get(id=carrier_request.carrier_plan.id)
            except:
                payment_details = None
                plan = None
            try:
                rating = Rating.objects.get(ship_request_id=carrier_request.id)
                review = Review.objects.get(ship_request_id=carrier_request.id)
            except:
                rating = None
                review = None
    except CarrierRequest.DoesNotExist:
        carrier_request = None

    if plan:
        try:
            current_location = CarrierCurrentLocation.objects.get(carrier_plan_id=plan.id)
        except:
            current_location = None

    try:
        shipment_status = ShipmentRequestTracking.objects.get(shipment=shipment)
    except:
        shipment_status = None


    shipper_alerts = get_carrier_alerts_accepted(request)
    num_requests = len(shipper_alerts)
    return render(request, "shipper/view_shipment_details.html", {'form': None, 'shipment': shipment,
                                                                  'shipper_alerts': shipper_alerts,
                                                                  'carrier_request': carrier_request,
                                                                  'current_location': current_location,
                                                                  'shipment_status': shipment_status,
                                                                  'rating': rating,
                                                                  'review': review,
                                                                  'payment_details': payment_details,
                                                                  'num_requests': num_requests})


def generate_estimate_plan(shipment, rate, plan):
    # estimated_value = random.randint(200, 400)
    current_date = datetime.today().date()
    t_rem = (plan.date_of_plan - current_date).days
    t_total = (plan.date_of_plan - plan.create_date.date()).days
    # t_rem, t_total = 5, 10  # t_rem = plan/shipment ki date - aaj ki date,  t_total = direct database main t_total calculate hokr save hojyega plan jb daaly ga


    weighted_rate = float(rate) / 1000
    # volumetric_rate = 0.000546
    fixed_cost = 20
    date_shipping = plan.date_of_plan.strftime("%Y-%m-%d")  # plan ki date

    # volume calculation
    shipment_volume = float(shipment.length * shipment.width * shipment.height)

    volumetric_weight = m3_to_cm3(shipment_volume) / 6000

    max_shipment_weight = max(float(shipment.weight), volumetric_weight)

    shipment_origin = shipment.pickup_location.split(',')
    shipment_destination = shipment.drop_off_location.split(',')

    # Define the coordinates of the two points
    origin = shipment.pickup_location  # (float(request.POST.get('origin[lat]')),float(request.POST.get('origin[long]')))  # (40.712776, -74.005974)  # New York City
    destination = shipment.drop_off_location  # (float(request.POST.get('destination[lat]')),float(request.POST.get('destination[long]')))  # (34.052235, -118.243683)  # Los Angeles

    # finding the Distance
    gmaps = googlemaps.Client(key=apikey)

    # Use the distance_matrix function to get distance information
    distance_result = gmaps.distance_matrix(origin, destination, mode='driving')

    # Extract the distance in meters
    distance = distance_result['rows'][0]['elements'][0]['distance']['value']

    # Convert distance from meters to kilometers
    distance_m = distance  # / 1000
    print("****Distance****")
    print(distance_m)

    # calculating Urgency Factor

    # finding alpha

    alpha = get_alpha(date_shipping)

    if alpha != 0:
        urgency_factor = 1 + pow((t_rem / t_total), -alpha)
    else:
        urgency_factor = 1

    estimated_value = (fixed_cost + (weighted_rate * max_shipment_weight) * distance_m)*urgency_factor

    estimated_value = validate_quotation(estimated_value)
    return estimated_value


@login_required
@csrf_exempt
def generate_estimate(request):
    # estimated_value = random.randint(200, 400)

    weighted_rate = 0.0000175
    # volumetric_rate = 0.000546
    fixed_cost = 20
    # date_shipping = '2024-03-14'  # for alpha
    date_shipping = request.POST.get('pick_up_date')

    # volume calculation
    shipment_volume = float(request.POST.get('length')) * float(request.POST.get('width')) * float(
        request.POST.get('height'))
    if request.POST.get('length_unit') == 'in':
        shipment_volume = inch_cube_to_meter_cube(shipment_volume)
    elif request.POST.get('length_unit') == 'cm':
        shipment_volume = cm_cube_to_meter_cube(shipment_volume)
    else:
        print(shipment_volume)

    volumetric_weight = m3_to_cm3(shipment_volume) / 6000

    # shipment_weight calculation
    if request.POST.get('weight_unit') == 'lbs':
        shipment_weight = lbs_to_kg(float(request.POST.get('weight')))
    else:
        shipment_weight = float(request.POST.get('weight'))

    max_shipment_weight = max(shipment_weight, volumetric_weight)

    # Define the coordinates of the two points
    origin = (float(request.POST.get('origin[lat]')),
              float(request.POST.get('origin[long]')))  # (40.712776, -74.005974)  # New York City
    destination = (float(request.POST.get('destination[lat]')),
                   float(request.POST.get('destination[long]')))  # (34.052235, -118.243683)  # Los Angeles

    # finding the Distance
    gmaps = googlemaps.Client(key=apikey)

    # Use the distance_matrix function to get distance information
    distance_result = gmaps.distance_matrix(origin, destination, mode='driving')

    # Extract the distance in meters
    distance = distance_result['rows'][0]['elements'][0]['distance']['value']

    # Convert distance from meters to kilometers
    distance_m = distance  # / 1000
    print("****Distance****")
    print(distance_m)

    # calculating Urgency Factor

    # finding alpha

    alpha = get_alpha(date_shipping)

    if alpha != 0:
        urgency_factor = 1 + pow((0.5), -alpha)
    else:
        urgency_factor = 1

    estimated_value = (fixed_cost + (weighted_rate * max_shipment_weight) * distance_m)*urgency_factor

    estimated_value = validate_quotation(estimated_value)
    return JsonResponse({'value': estimated_value})

def get_alpha(date_str):

    date = datetime.strptime(date_str, '%Y-%m-%d')                                                                      # Convert input date string to a datetime object


    if date.weekday() in [5, 6]:  # Saturday (5) or Sunday (6)                                                          # Check if the date falls on a weekend
        return 1


    if 8 <= date.hour <= 10 or 17 <= date.hour <= 19:  # Assuming high traffic times are 8-10am and 5-7pm               # Check for high traffic times (you can customize this based on your criteria)
        return 1

    # Checking for holidays                                                                                             (you can customize this based on your criteria)
    if date.month == 12 and date.day in [24, 25, 31]:  # Christmas Eve, Christmas Day, New Year's Eve
        return 2
    if date.month == 1 and date.day == 1:  # New Year's Day
        return 2
    # Add more conditions for other seasonal holidays

    # If none of the above conditions are met, return 0 (no special events)
    return 0


def validate_quotation(estimated_quotation):
    # Round the estimated_quotation to two decimal places
    rounded_quotation = round(estimated_quotation, 2)
    return rounded_quotation


@login_required
@shipper_required
def user_shipments(request, status):
    user = request.user
    try:
        shipper_user = get_object_or_404(ShipperIndividual, user_id=request.user.id)
    except:
        message = "Shipper User ID is invalid";
    # Retrieve all shipments for the user
    shipments = Shipment.objects.filter(shipper_user=shipper_user, status__icontains=status).order_by('-id')
    num_shipments = len(shipments)

    shipper_alerts = get_carrier_alerts_accepted(request)
    num_requests = len(shipper_alerts)

    latest_request = CarrierRequest.objects.filter(
        shipment_id=OuterRef('pk')
    ).order_by('-date')

    # Query to fetch all shipments along with their latest carrier request (if any)
    shipments = Shipment.objects.filter(shipper_user=shipper_user, status=status).order_by('-id').annotate(
        latest_request_status=Subquery(latest_request.values('status')[:1]),
        latest_request_id=Subquery(latest_request.values('id'))
    )

    if status == 'assigned':
        shipments = get_shipments_with_payment_details(user, 'paid')

    if status == 'payment Pending':
        payment_status = 'isActive'
    else:
        payment_status = None

    return render(request, "shipper/user_shipments.html", {'form': None, 'shipments': shipments,
                                                           'num_shipments': num_shipments,
                                                           'shipper_alerts': shipper_alerts,
                                                           'num_requests': num_requests,
                                                           status: 'isActive', 'payment_status': payment_status,
                                                           'menu_item_shipper_shipments': 'active'})


def chatbot_window(request):
    list_of_ques = ["What do I do if my package shows as delivered, but it's not here?",
                    "Do you offer international shipping?", " Can I set a specific time for my delivery?",
                    " Do you offer expedited shipping options?", "What is the process of shipping through Truckpool?"]

    '''list_of_ques = ['Hi', 'Bye', 'Thanks', 'Who are you?', 
                        'what is your name', 'Could you help me?', 'I need to create a new account', 
                        'have a complaint', 'How can I check the shipping cost for my order?', 
                        'What carriers do you use for shipping?', 'Is it possible to schedule a specific delivery time?', 
                        'How long does it take to process a refund?', 'Do you offer international shipping?', 
                        'Can I change the shipping method after placing my order?', 
                        "What should I do if my package is marked as delivered but I haven't received it?", 
                        'Is there a way to request signature confirmation upon delivery?', 
                        'How can I track multiple packages from the same order?', 
                        'I need to cancel my order. How can I do that?', 
                        'Can I speak to a customer care representative?', 
                        'How do I contact your customer support outside of this chat?', 
                        'My package seems to be delayed. Can you help me understand why?', 
                        'Do you offer expedited shipping options?', 
                        'Can I change the delivery address for my order?', 
                        'What is the process of shipping through Truckpool?']'''

    return render(request, 'shipper/chatbot_window.html', {'questions': list_of_ques})


def get_shipments_with_payment_details(shipper_user, status):
    # Get the CarrierRequest objects with the specified status
    carrier_requests = CarrierRequest.objects.filter(status=status)

    # Extract the shipment IDs from the CarrierRequest objects
    shipment_ids = carrier_requests.values_list('shipment_id', flat=True).order_by('-id')

    # Annotate the Shipments queryset with the total amount from PaymentDetails
    shipments_with_payment = (
        Shipment.objects
        .filter(shipper_user=shipper_user.shipperindividual, id__in=shipment_ids).order_by('-id')
        .annotate(amount=Sum('carrierrequest__paymentdetails__amount'))
    )

    return shipments_with_payment


def inch_cube_to_meter_cube(inch_cube):
    # 1 inch = 0.0254 meters (conversion factor for length)
    # Therefore, (1 inch)^3 = (0.0254 meters)^3
    cubic_meter_conversion_factor = (0.0254) ** 3
    meter_cube = inch_cube * cubic_meter_conversion_factor
    return meter_cube


def cm_cube_to_meter_cube(cm_cube):
    # 1 cm = 0.01 meters (conversion factor for length)
    # Therefore, (1 cm)^3 = (0.01 meters)^3
    cubic_meter_conversion_factor = (0.01) ** 3
    meter_cube = cm_cube * cubic_meter_conversion_factor
    return meter_cube


def m3_to_cm3(volume_m3):
    """
    Convert volume from cubic meters (m³) to cubic centimeters (cm³).

    Parameters:
        volume_m3 (float): Volume in cubic meters (m³).

    Returns:
        float: Volume converted to cubic centimeters (cm³).
    """
    volume_cm3 = volume_m3 * 1000000  # 1 m³ = 1000000 cm³
    return volume_cm3


def lbs_to_kg(lbs):
    # 1 pound = 0.453592 kilograms
    kg = lbs * 0.453592
    return round(kg, 2)


def match_with_carrier(request, shipment):
    packer = None
    covering_radius = 30000  # It is the distance range to shortlist carriers
    date = request.POST.get('pick_up_date')
    # shipment_volume = float(shipment.length) * float(shipment.width) * float(shipment.height)
    # carriersPlans = CarrierPlan.objects.filter(date_of_plan=shipment.pickup_date, start_city=shipment.pickup_city,
    # end_city=shipment.drop_off_city, space_available__gt=shipment_volume)

    plans_to_show = []
    # all plans that are open
    carriers_plans = CarrierPlan.objects.filter(date_of_plan=shipment.pickup_date, status='Open')

    gmaps = googlemaps.Client(key=apikey)

    for plan in carriers_plans:
        carrier = plan.carrier_user  # get carrier of plan

        vehicle = carrier.vehicle_type  # get  vehicle Type

        ########## Matching the locations -- Start ########

        plan_origin = plan.start_location
        plan_destination = plan.end_location

        shipment_origin = shipment.pickup_location
        shipment_destination = shipment.drop_off_location

        origin_distance = gmaps.distance_matrix(plan_origin, shipment_origin)['rows'][0]['elements'][0]['distance'][
            'value']
        dest_distance = \
            gmaps.distance_matrix(shipment_destination, plan_destination)['rows'][0]['elements'][0]['distance']['value']

        ########## Matching the locations -- end ##########

        if ((origin_distance <= covering_radius) or (plan.start_city == shipment.pickup_city)) & (
                (dest_distance <= covering_radius) or (plan.end_city == shipment.drop_off_city)):
            ########## Fitting into vehicle -- Start ########
            figure, packer = load_truck(shipment, plan, carrier, vehicle, False)
            # figure.show()

            print(f'number of unfit items: {len(packer.unfit_items)}')

            ########## Fitting into vehicle -- end ##########

            if (len(packer.unfit_items) == 0):
                plans_to_show.append(plan)
                print(len(plans_to_show))

    return plans_to_show


def load_truck(shipment, plan, carrier, vehicle, from_shipment_view):
    fig = None
    packer = Packer()

    # carrier dimensions
    # vehicle_type = df_carrier['vehicle_type'].iloc[0] covered in vehicle
    initial_available_perc = (plan.space_available) / 100  # df_carrier['initial_%_avbl'].iloc[0]
    c_width = vehicle.length * 10  # 8 #vehicle.width                     #df_std_trucks.loc[df_std_trucks['code'] == vehicle_type]['width'].iloc[0]
    c_height = vehicle.width * 10  # 14 #vehicle.height                   #df_std_trucks.loc[df_std_trucks['code'] == vehicle_type]['height'].iloc[0]
    c_depth = vehicle.height * 10  # 3 #vehicle.length                    #df_std_trucks.loc[df_std_trucks['code'] == vehicle_type]['length'].iloc[0]
    c_weight = vehicle.weight
    #  init bin
    box = Bin(
        (str(plan.carrier_user_id) + "\n" + carrier.first_name + carrier.last_name + " \n" + str(plan.date_of_plan)),
        (c_width, c_height, c_depth),
        c_weight,  # plug weights
        0,
        0)
    packer.addBin(box)

    distinct_colors = [
        "#FFFF37",  # Yellow
        "#00FFFF",  # Cyan
        "#FF00FF",  # Magenta
        "#0000FF",  # Blue
        "#008000",  # Green
        "#800080",  # Purple
        "#FFA500",  # Orange
        "#800000",  # Maroon
        "#008080",  # Teal
        "#FFFFFF",  # White
        "#FFD700",  # Gold
        "#00FF00",  # Lime
        "#9400D3"  # DarkViolet
    ]

    # Here we will add the carrier's own load first
    carrier_load = Item(
        partno='my_consignment',  # partno / PN of item (unique value) # we'll map Shipment ID here
        name='own_load',
        # type of item                       # _Shipper ID_NAME_Pickup-coordinates_Delivery-coordinates
        typeof='cube',  # cube or cylinder
        WHD=((c_width * (1 - initial_available_perc)), c_height, c_depth),  # (width , height , depth)           #
        weight=vehicle.weight * (1 - initial_available_perc),  # item weight                        # item weight
        level=1,  # priority (Item need to pack)
        loadbear=120,  # item bearing
        updown=False,  # item fall down or not              # True means the item can be placed upside down.
        color="#000000"  # set item color , you also can use color='red' or color='r'
    )

    packer.addItem(carrier_load)

    active_shipment_ids_current_plan = (CarrierRequest.objects
                                        .filter(carrier_plan_id=plan.id,
                                                status__in=['accepted', 'pending', 'paid'])
                                        .values_list('shipment_id', flat=True))

    active_shipments = Shipment.objects.filter(id__in=active_shipment_ids_current_plan)
    color_index = 0
    for active_shipment in active_shipments:
        if (shipment.id != active_shipment.id):
            item1 = Item(
                partno=active_shipment.id,
                # 'testItem',                 # partno / PN of item (unique value) # we'll map Shipment ID here
                name=active_shipment.shipper_user.first_name + active_shipment.shipper_user.last_name,
                # 'wash',                         # type of item                       # _Shipper ID_NAME_Pickup-coordinates_Delivery-coordinates
                typeof='cube',  # cube or cylinder
                WHD=(active_shipment.length * 10, active_shipment.width * 10, active_shipment.height * 10),
                # (width , height , depth)           #
                weight=active_shipment.weight,  # item weight                        # item weight
                level=2,  # priority (Item need to pack)
                loadbear=1000,  # item bearing
                updown=True,  # item fall down or not              # True means the item can be placed upside down.
                color=distinct_colors[color_index]  # set item color , you also can use color='red' or color='r'
            )
            packer.addItem(item1)
            color_index += 1
        print(active_shipment)

    # current shipment to be added will be added to packer here
    packer.addItem(Item(
        partno=shipment.id,
        # 'testItem',                 # partno / PN of item (unique value) # we'll map Shipment ID here
        name=shipment.shipper_user.first_name + shipment.shipper_user.last_name,
        # 'wash',                         # type of item                       # _Shipper ID_NAME_Pickup-coordinates_Delivery-coordinates
        typeof='cube',  # cube or cylinder
        WHD=(shipment.length * 10, shipment.width * 10, shipment.height * 10),  # (width , height , depth)           #
        weight=shipment.weight,  # item weight                        # item weight
        level=2,  # priority (Item need to pack)
        loadbear=1000,  # item bearing
        updown=True,  # item fall down or not              # True means the item can be placed upside down.
        color='red'  # set item color , you also can use color='red' or color='r'
    ))

    # calculate packing
    packer.pack(
        bigger_first=True,
        fix_point=True,
        distribute_items=True,
        check_stable=True,
        support_surface_ratio=0.75,
        number_of_decimals=3
    )

    # paint the results

    for b in packer.bins:
        painter = Painter(b)
        fig = painter.plotBoxAndItems(
            title=b.partno,
            alpha=0.2,
            write_num=True,
            fontsize=10
        )

    return fig, packer


def inches_to_meters(inches):
    meters = inches / 39.37
    return round(meters, 2)


def cm_to_meter(cm):
    meter = cm / 100
    return round(meter, 2)


@login_required
@csrf_exempt
def book_carrier(request):
    if request.method == 'POST':
        shipment_id = int(request.POST.get('shipment_id'))
        carrier_user_id = int(request.POST.get('carrier_user_id'))
        plan_id = int(request.POST.get('plan_id'))
        calculated_quote = float(request.POST.get('calculated_quote'))

        carrier = get_object_or_404(Carrier, user_id=carrier_user_id)
        plan = get_object_or_404(CarrierPlan, id=plan_id)

        # carrier = Carrier.objects.(carrier_user_id).first()

        # Create a new CarrierRequest instance with pending status
        new_request = CarrierRequest.objects.create(
            carrier_id=carrier.id,
            carrier_plan_id=plan.id,
            shipment_id=shipment_id,
            quote=calculated_quote,
            status='pending'
        )

        # Prepare response data
        response_data = {
            'success': True,
            'book_message': 'Request sent successfully.',
            'request_id': new_request.id  # Optional: Return the ID of the created request
        }
        return JsonResponse(response_data)
    else:
        # Return an error response for non-POST requests
        response_data = {
            'success': False,
            'book_message': 'Invalid request method.'
        }
        return JsonResponse(response_data, status=405)  # 405 Method Not Allowed


def payment_view(request, request_id):
    success_message = 'Payment Successful.'
    carrier_request = CarrierRequest.objects.get(pk=request_id)
    shipment_id = carrier_request.shipment_id

    try:
        shipment = get_object_or_404(Shipment, pk=shipment_id)
    except:
        shipment = None

    if request.method == 'POST':
        form = PaymentDetailsForm(request.POST)
        # form.instance.expiration_date = '' + request.POST.get('expiry_mm') + '/' + request.POST.get('expiry_yy')
        # form.instance.amount = '100'
        if form.is_valid():
            payment_details = form.save()
            # Optionally, perform additional actions after saving the data

            # update status of shipment.
            shipment.status = 'assigned'
            shipment.save()

            # update status of request.
            carrier_request.status = 'paid'
            carrier_request.save()

            return render(request, 'shipper/payment_success.html', {'success_message': success_message})
    else:
        form = PaymentDetailsForm()

    return render(request, "shipper/payment_view.html",
                  {'form': form, 'shipment_request': carrier_request, 'shipment': shipment,
                   'user_message': form.errors})


def pay_now(request, request_id):
    carrier_request = CarrierRequest.objects.get(pk=request_id)
    shipment_id = carrier_request.shipment_id

    try:
        shipment = get_object_or_404(Shipment, pk=shipment_id)
    except:
        shipment = None

    message = 'Payment Successful.'
    return render(request, "shipper/payment_view.html",
                  {'message': message, 'shipment': shipment, 'carrier_request': carrier_request})


def payment_success(request):
    return render(request, 'shipper/payment_success.html')


@login_required
@csrf_exempt
def submit_review(request):
    print(request)
    rating = int(request.POST.get('rating'))
    review = request.POST.get('review')
    shipment_id = int(request.POST.get('shipment_id'))
    carrier_request_id = int(request.POST.get('carrier_request_id'))
    rating_id = request.POST.get('rating_id')
    review_id = request.POST.get('review_id')

    if rating_id:
        rating_obj = Rating.objects.get(pk=int(rating_id))
        rating_obj.rating = rating
        rating_obj.save()
    else:
        rating_obj = Rating.objects.create(shipper_user=request.user, ship_request_id=carrier_request_id, rating=rating)

    if review_id:
        review_obj = Review.objects.get(pk=int(review_id))
        review_obj.text = review
        review_obj.save()
    else:
        review_obj = Review.objects.create(shipper_user=request.user, ship_request_id=carrier_request_id, text=review)

    # rating = Rating.objects.create(shipper_user=request.user, ship_request_id=carrier_request_id, rating=rating)
    # review = Review.objects.create(shipper_user=request.user, ship_request_id=carrier_request_id, text=review)
    return JsonResponse({'msg': 'Review submitted successfully.'})


def retrieve_rating_carrier(carrier):
    carrier_request_completed = CarrierRequest.objects.filter(carrier_id=carrier.id, status='fulfilled').values_list(
        'id', flat=True)

    carrier_ratings = Rating.objects.filter(ship_request__in=carrier_request_completed)
    average_rating = carrier_ratings.aggregate(Avg('rating'))['rating__avg']

    print(carrier_ratings)
    print(average_rating)

    if average_rating ==None:
        average_rating = 0
    return average_rating

def retrieve_carrier_reviews(carrier):
    carrier_request_completed = CarrierRequest.objects.filter(carrier_id=carrier.id, status='fulfilled').values_list(
        'id', flat=True).order_by('-id')

    carrier_reviews = Review.objects.filter(ship_request__in=carrier_request_completed).order_by('-id')
    return carrier_reviews

@csrf_exempt
def view_carrier_profile(request):
    carrier_user_id = request.POST.get('carrier_id')

    carrier_instance = None
    rating = None
    if carrier_user_id:
        try:
            carrier_instance = get_object_or_404(Carrier, user_id=carrier_user_id)
            rating = retrieve_rating_carrier(carrier_instance)
            review = retrieve_carrier_reviews(carrier_instance)
        except:
            carrier_instance = None
            rating = None

    return render(request, 'carrier/carrier_profile_template.html',
                      {'carrier': carrier_instance,
                       'rating': rating,'reviews': review, })
