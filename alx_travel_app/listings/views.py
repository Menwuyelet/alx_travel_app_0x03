from django.shortcuts import render
from rest_framework import viewsets
from .models import Listing, Booking, Review, Payment
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer, PaymentSerializer
from django.shortcuts import get_object_or_404
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking
import uuid
from .tasks import send_booking_confirmation_email
# Create your views here.

class ListingViewset(viewsets.ModelViewSet):
    serializer_class = [ListingSerializer]
    queryset = Booking.objects.all()

    def perform_create(self, serializer):
        listing = serializer.save()
        listing.user.add(self.request.user)

class BookingViewset(viewsets.ModelViewSet):
    serializer_class = [BookingSerializer]

    def perform_create(self, serializer):
        listing_id = self.request.data.get('listing_id')
        listing = get_object_or_404(Listing, id=listing_id)
        booking = serializer.save(user=self.request.user, listing=listing)
        send_booking_confirmation_email.delay(
            booking.user.email, str(booking.id)
        )



class InitiatePaymentView(APIView):
    def post(self, request):
        amount = request.data.get("amount")
        booking_reference = request.data.get("booking_reference")

        # Create unique transaction reference
        tx_ref = str(uuid.uuid4())

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "amount": str(amount),
            "currency": "ETB",
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "tx_ref": tx_ref,
            "callback_url": "http://localhost:8000/api/payments/verify/",
            "return_url": "http://localhost:8000/payment-success/",  # Frontend redirect
            "customization": {
                "title": "Booking Payment",
                "description": f"Payment for booking {booking_reference}"
            }
        }

        response = requests.post(
            f"{settings.CHAPA_BASE_URL}/transaction/initialize",
            headers=headers,
            json=data
        )

        chapa_response = response.json()

        if response.status_code == 200 and chapa_response.get("status") == "success":
            payment = Payment.objects.create(
                user=request.user,
                booking_reference=booking_reference,
                transaction_id=tx_ref,
                amount=amount,
                status="Pending"
            )
            return Response({
                "checkout_url": chapa_response["data"]["checkout_url"],
                "transaction_id": tx_ref
            })
        return Response(chapa_response, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyPaymentView(APIView):
    def get(self, request):
        tx_ref = request.query_params.get("transaction_id")

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        }

        response = requests.get(
            f"{settings.CHAPA_BASE_URL}/transaction/verify/{tx_ref}",
            headers=headers
        )

        chapa_response = response.json()

        try:
            payment = Payment.objects.get(transaction_id=tx_ref)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        if response.status_code == 200 and chapa_response.get("status") == "success":
            status_from_chapa = chapa_response["data"]["status"]

            if status_from_chapa == "success":
                payment.status = "Completed"
            else:
                payment.status = "Failed"

            payment.save()

        return Response({
            "payment_status": payment.status,
            "details": chapa_response
        })