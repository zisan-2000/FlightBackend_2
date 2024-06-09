from django.urls import path
from . import views
from .views import FlightOffersAPIView, MetricsAPIView, CheapestFlightAPIView


urlpatterns = [

    path('api/flight_offers/', FlightOffersAPIView.as_view(), name='flight_offers_api'),
    path('api/metrics/', MetricsAPIView.as_view(), name='metrics_api'),
    path('api/cheapest_flight/', CheapestFlightAPIView.as_view(), name='cheapest_flight_api'),
    # other urls...
    path('', views.flight_offers, name='flight_offers'),
    path('origin_airport_search/', views.origin_airport_search, name='origin_airport_search'),
    path('destination_airport_search/', views.destination_airport_search, name='destination_airport_search')
]

