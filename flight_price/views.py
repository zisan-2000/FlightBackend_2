import json
from amadeus import Client, ResponseError, Location
from django.shortcuts import render
from django.contrib import messages
from .flight import Flight
from .metrics import Metrics
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FlightOfferSerializer, MetricsSerializer

amadeus = Client(client_id='d0e64LqY4WYl0De6O0xfc5nq2Lp82kdu', client_secret='6rSoF5CXVQvQrsum')

# Declare global variables
flight_offers = []
metrics = {}
cheapest_flight = 0.0





def flight_offers(request):
    global flight_offers, metrics, cheapest_flight
    origin = request.POST.get('Origin')
    destination = request.POST.get('Destination')
    departure_date = request.POST.get('Departuredate')
    return_date = request.POST.get('Returndate')

    kwargs = {'originLocationCode': origin,
              'destinationLocationCode': destination,
              'departureDate': departure_date,
              'adults': 1
              }

    kwargs_metrics = {'originIataCode': origin,
                      'destinationIataCode': destination,
                      'departureDate': departure_date
                      }
    trip_purpose = ''
    try:
        if return_date:
            kwargs['returnDate'] = return_date
            kwargs_trip_purpose = {'originLocationCode': origin,
                                   'destinationLocationCode': destination,
                                   'departureDate': departure_date,
                                   'returnDate': return_date
                                   }

            trip_purpose = get_trip_purpose(**kwargs_trip_purpose)
        else:
            kwargs_metrics['oneWay'] = 'true'

        if origin and destination and departure_date:
            flight_offers = get_flight_offers(**kwargs)
            print("flight_offers")
            print("flight_offers")
            print("flight_offers")
            print(flight_offers)
            metrics = get_flight_price_metrics(**kwargs_metrics)
            print("metrics")
            print(metrics)
            cheapest_flight = get_cheapest_flight_price(flight_offers)
            print("cheapest_flight")
            print(cheapest_flight)
            is_good_deal = ''
            if metrics is not None:
                is_good_deal = rank_cheapest_flight(cheapest_flight, metrics['first'], metrics['third'])
                is_cheapest_flight_out_of_range(cheapest_flight, metrics)

            return render(request, 'flight_price/results.html', {'flight_offers': flight_offers,
                                                                 'origin': origin,
                                                                 'destination': destination,
                                                                 'departure_date': departure_date,
                                                                 'return_date': return_date,
                                                                 'trip_purpose': trip_purpose,
                                                                 'metrics': metrics,
                                                                 'cheapest_flight': cheapest_flight,
                                                                 'is_good_deal': is_good_deal
                                                                 })
    except ResponseError as error:
        messages.add_message(request, messages.ERROR, error.response.result['errors'][0]['detail'])
        return render(request, 'flight_price/home.html', {})
    return render(request, 'flight_price/home.html', {})



class FlightOffersAPIView(APIView):
    def get(self, request):
        global flight_offers
        serializer = FlightOfferSerializer(flight_offers, many=True)
        return Response(serializer.data)

class MetricsAPIView(APIView):
    def get(self, request):
        global metrics
        serializer = MetricsSerializer(metrics)
        return Response(serializer.data)

class CheapestFlightAPIView(APIView):
    def get(self, request):
        global cheapest_flight
        return Response({'cheapest_flight': cheapest_flight})





def get_flight_offers(**kwargs):
    global amadeus
    search_flights = amadeus.shopping.flight_offers_search.get(**kwargs)
    flight_offers = []
    for flight in search_flights.data:
        offer = Flight(flight).construct_flights()
        flight_offers.append(offer)
    return flight_offers


def get_flight_price_metrics(**kwargs_metrics):
    global amadeus
    kwargs_metrics['currencyCode'] = 'USD'
    metrics = amadeus.analytics.itinerary_price_metrics.get(**kwargs_metrics)
    return Metrics(metrics.data).construct_metrics()


def get_trip_purpose(**kwargs_trip_purpose):
    global amadeus
    trip_purpose = amadeus.travel.predictions.trip_purpose.get(**kwargs_trip_purpose).data
    return trip_purpose['result']


def get_cheapest_flight_price(flight_offers):
    return flight_offers[0]['price']


def rank_cheapest_flight(cheapest_flight_price, first_price, third_price):
    cheapest_flight_price_to_number = float(cheapest_flight_price)
    first_price_to_number = float(first_price)
    third_price_to_number = float(third_price)
    if cheapest_flight_price_to_number < first_price_to_number:
        return 'A GOOD DEAL'
    elif cheapest_flight_price_to_number > third_price_to_number:
        return 'HIGH'
    else:
        return 'TYPICAL'


def is_cheapest_flight_out_of_range(cheapest_flight_price, metrics):
    min_price = float(metrics['min'])
    max_price = float(metrics['max'])
    cheapest_flight_price_to_number = float(cheapest_flight_price)
    if cheapest_flight_price_to_number < min_price:
        metrics['min'] = cheapest_flight_price
    elif cheapest_flight_price_to_number > max_price:
        metrics['max'] = cheapest_flight_price


def origin_airport_search(request):
    global amadeus
    if request.is_ajax():
        try:
            data = amadeus.reference_data.locations.get(keyword=request.GET.get('term', None),
                                                        subType=Location.ANY).data
        except ResponseError as error:
            messages.add_message(request, messages.ERROR, error.response.result['errors'][0]['detail'])
    return HttpResponse(get_city_airport_list(data), 'application/json')


def destination_airport_search(request):
    global amadeus
    if request.is_ajax():
        try:
            data = amadeus.reference_data.locations.get(keyword=request.GET.get('term', None),
                                                        subType=Location.ANY).data
        except ResponseError as error:
            messages.add_message(request, messages.ERROR, error.response.result['errors'][0]['detail'])
    return HttpResponse(get_city_airport_list(data), 'application/json')


def get_city_airport_list(data):
    result = []
    for i, val in enumerate(data):
        result.append(data[i]['iataCode'] + ', ' + data[i]['name'])
    result = list(dict.fromkeys(result))
    return json.dumps(result)
