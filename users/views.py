import datetime

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from .decorators import carrier_required, shipper_required
from .forms import CarrierUserCreationForm, CarrierRegistrationForm, ShipperBusinessRegistrationForm, \
    ShipperIndividualRegistrationForm, ShipperUserCreationForm, CustomAuthenticationForm
from .models import Carrier
from shipper.models import CarrierRequest, Shipment

import json
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder

import random
import pickle

#### Loading files for Chatbot####

'''with open("./TruckPool_Django/intents.json") as file:
    data = json.load(file)

model = keras.models.load_model('./TruckPool_Django/chat_model')

with open('./TruckPool_Django/tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

with open('./TruckPool_Django/label_encoder.pickle', 'rb') as enc:
        lbl_encoder = pickle.load(enc)
'''

# Load the TensorFlow Lite model
interpreter = tf.lite.Interpreter(model_path='./TruckPool_Django/TP_chatbot_model.tflite')
interpreter.allocate_tensors()

# Load tokenizer and label encoder
with open('./TruckPool_Django/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

with open('./TruckPool_Django/label_encoder.pickle', 'rb') as enc:
    lbl_encoder = pickle.load(enc)

# parameters
max_len = 20

#### End Loading files for Chatbot####


def index(request):
    return render(request, 'users/index.html')


def carrier_signup(request):
    return render(request, 'users/carrier_signup.html')


@login_required
@carrier_required
def carrier_view(request):
    carrier_alerts = get_carrier_alerts(request)
    num_requests = len(carrier_alerts)

    return render(request, "carrier/carrier_view.html",
                  {'carrier_requests': carrier_alerts, 'num_requests': num_requests})


# Create your views here.
@login_required
@shipper_required
def shipper_view(request):
    shipper_alerts = get_carrier_alerts_accepted(request)
    num_requests = len(shipper_alerts)

    return render(request, "shipper/shipper_view.html",
                  {'shipper_alerts': shipper_alerts, 'num_requests': num_requests})


def register_carrier(request):
    user_message = ''
    success_message = ''
    if request.method == 'POST':
        user_form = CarrierUserCreationForm(request.POST)
        carrier_form = CarrierRegistrationForm(request.POST)

        # user_message = user_form.error_messages

        if user_form.is_valid() and carrier_form.is_valid():
            user = user_form.save()
            carrier = carrier_form.save(commit=False)
            carrier.user = user
            carrier.save()
            success_message = "Carrier Registered Successfully."
            return render(request, 'users/success_registration.html', {'success_message': success_message})
            # return redirect('carrier_signup')  # Redirect to login page after successful registration
        else:
            user_message = user_form.errors
    else:
        user_form = CarrierUserCreationForm()
        carrier_form = CarrierRegistrationForm()

    return render(request, 'users/carrier_signup.html',
                  {'user_form': user_form,
                   'carrier_form': carrier_form,
                   'user_message': user_message,
                   # 'carrier_message': carrier_form.
                   'success_message': success_message
                   })


def signin_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            # Get the user credentials from the form
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Authenticate the user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Log in the user
                login(request, user)
                messages.success(request, 'Login successful.')
                # Redirect based on user type
                if hasattr(user, 'shipperindividual'):
                    return render(request, 'shipper/shipper_view.html')
                elif hasattr(user, 'shipperbusiness'):
                    return render(request, 'shipper/shipper_view.html')
                elif hasattr(user, 'carrier'):
                    return redirect('carrier_view')
            else:
                messages.error(request, 'Invalid username or password.')

    else:
        form = CustomAuthenticationForm()

    return render(request, 'users/login.html', {'form': form, 'user_message': form.errors})


def logout_view(request):
    logout(request)
    return redirect('signin')


def success_registration(request):
    return render(request, 'users/success_registration.html')


def register_shipper(request):
    user_message = ''
    success_message = ''
    if request.method == 'POST':
        user_form = ShipperUserCreationForm(request.POST)
        shipper_ind_form = ShipperIndividualRegistrationForm(request.POST)
        shipper_bus_form = ShipperBusinessRegistrationForm(request.POST)

        # user_message = user_form.error_messages

        if user_form.is_valid() and shipper_ind_form.is_valid():
            user = user_form.save()
            shipper = shipper_ind_form.save(commit=False)
            shipper.user = user
            shipper.save()
            success_message = "Shipper Registered Successfully."
            return render(request, 'users/shipper_success.html', {'success_message': success_message})
            # return redirect('carrier_signup')  # Redirect to login page after successful registration
        elif user_form.is_valid() and shipper_bus_form.is_valid():
            user = user_form.save()
            shipper = shipper_bus_form.save(commit=False)
            shipper.user = user
            shipper.save()
            success_message = "Shipper Registered Successfully."
            return render(request, 'users/shipper_success.html', {'success_message': success_message})
        else:
            user_message = user_form.errors
    else:
        user_form = ShipperUserCreationForm()
        shipper_ind_form = ShipperIndividualRegistrationForm()
        shipper_bus_form = ShipperBusinessRegistrationForm()

    return render(request, 'users/shipper_signup.html',
                  {'user_form': user_form,
                   'shipper_ind_form': shipper_ind_form,
                   'shipper_bus_form': shipper_bus_form,
                   'user_message': user_message,
                   # 'carrier_message': carrier_form.
                   'success_message': success_message
                   })


def forbidden_page(request):
    return render(request, 'users/forbidden_page.html')


def get_carrier_alerts(request):
    try:
        carrier_instance = get_object_or_404(Carrier, user_id=request.user.id)
    except:
        carrier_instance = None

    if carrier_instance:
        carrier_requests_new = CarrierRequest.objects.filter(carrier_id=carrier_instance.id, status='pending').order_by('-id')
    else:
        carrier_requests_new = []

    return carrier_requests_new


def get_carrier_alerts_accepted(request):
    shipments = Shipment.objects.filter(shipper_user=request.user.id).values_list('id', flat=True)

    if shipments:
        carrier_requests_new = CarrierRequest.objects.filter(shipment_id_in=shipments, status_in=['accepted', 'rejected']).order_by('-id')
    else:
        carrier_requests_new = []

    return carrier_requests_new


@login_required
@csrf_exempt
def chat_with_bot(request):
    message = request.POST.get('message')

    #result = model.predict(keras.preprocessing.sequence.pad_sequences(
    #    tokenizer.texts_to_sequences([message]),
    #    truncating='post', maxlen=max_len))

    #tag = lbl_encoder.inverse_transform([np.argmax(result)])

    #for i in data['intents']:
    #    if i['tag'] == tag:
    #        reply_message = np.random.choice(i['responses'])
    #    else:
    #        reply_message = 'Sorry, please rephrase your query'



    # Prepare input data
    input_text = message
    input_sequence = tokenizer.texts_to_sequences([input_text])
    padded_input_sequence = tf.keras.preprocessing.sequence.pad_sequences(input_sequence, truncating='post',
                                                                          maxlen=max_len)

    padded_input_sequence = padded_input_sequence.astype(np.float32)

    # Set input tensor
    input_index = interpreter.get_input_details()[0]['index']
    interpreter.set_tensor(input_index, padded_input_sequence)

    # Run inference
    interpreter.invoke()

    # Get output tensor
    output_index = interpreter.get_output_details()[0]['index']
    output_data = interpreter.get_tensor(output_index)

    # Decode the predicted tag
    tag = lbl_encoder.inverse_transform([np.argmax(output_data)])

    # Load intents JSON data
    with open("./TruckPool_Django/intents.json") as file:
        data = json.load(file)

    # Retrieve and print the response for the predicted tag
    for intent in data['intents']:
        if intent['tag'] == tag[0]:
            reply_message = np.random.choice(intent['responses'])
        #else:
        #   reply_message = 'Sorry, please rephrase your query'

    # reply_message = 'I will Tell you'

    ########### code to simply match questions START##################
    '''intents_file = './TruckPool_Django/intents.json'
    intents_data = load_intents(intents_file)

    #user_input = input("Enter your message: ")
    
    reply_message = match_input_with_patterns(message, intents_data)'''
    ########### code to simply match questions START##################

    response_data = {
        'username': 'abc',
        'avatar-user': 'user',
        'avatar-chat': 'chatbot',
        'message': reply_message,
        'time': str(datetime.datetime),
        'image_url': '../static/images/icons/robot.png',
        'is_reply': True,
    }

    return JsonResponse(response_data)

def load_intents(intents_file):
    with open(intents_file, 'r') as file:
        intents_data = json.load(file)
    return intents_data

def match_input_with_patterns(user_input, intents_data):
    for intent in intents_data['intents']:
        for pattern in intent['patterns']:
            if user_input.lower() == pattern.lower():
                return intent['responses'][0]  # Return the first response for the matched pattern
    return "I'm sorry, I didn't understand that."