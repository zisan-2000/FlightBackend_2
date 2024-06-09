# In your Django app's serializers.py

from rest_framework import serializers

class FlightOfferSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    id = serializers.IntegerField()
    
    # Add other fields as needed

class MetricsSerializer(serializers.Serializer):
    min = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    first = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    median = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    third = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)