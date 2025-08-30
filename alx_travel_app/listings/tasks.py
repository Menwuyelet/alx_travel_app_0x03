from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_payment_confirmation_email(user_email, booking_reference, amount):
    subject = "Payment Successful"
    message = f"Your payment of {amount} for booking {booking_reference} was successful."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])