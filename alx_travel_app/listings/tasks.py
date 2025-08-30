from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_payment_confirmation_email(user_email, booking_reference, amount):
    subject = "Payment Successful"
    message = f"Your payment of {amount} for booking {booking_reference} was successful."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

@shared_task
def send_booking_confirmation_email(user_email, booking_id):
    subject = "Booking Confirmation"
    message = f"Your booking with ID {booking_id} has been confirmed!"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    
    send_mail(subject, message, from_email, recipient_list)
    return f"Email sent to {user_email} for booking {booking_id}"