from rest_framework import serializers
from .models import Listing, Booking, Review, Payment

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['user', 'title', 'description', 'location', 'price_per_night', 'available']
        read_only_fields = ['user']

    def create(self, validated_data):
        property = Listing.objects.create(validated_data)
        return property


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    listing = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = ['user', 'listing' 'check_in', 'check_out']

    def create(self, validated_data):
        booking = Booking.objects.create(validated_data)
        return booking

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    listing = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['listing', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        review = Review.objects.create(validated_data)
        return review
    

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["status", "transaction_id", "created_at"]