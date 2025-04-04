from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from celery.schedules import crontab
from datetime import datetime

@shared_task
def send_email_task(subject, message, recipient_list):
    """
    Celery task to send emails asynchronously
    """
    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipient_list,
        fail_silently=False,
    )

@shared_task
def send_registration_email(user_email, username):
    """
    Task to send a registration confirmation email
    """
    subject = "Welcome to Our Platform"
    message = f"Hello {username},\n\nThank you for registering with us. Your account has been successfully created."
    recipient_list = [user_email]
    
    return send_email_task(subject, message, recipient_list)

@shared_task
def send_product_registration_email(user_email, product_name):
    """
    Task to send a product registration confirmation email
    """
    subject = "Product Registration Confirmation"
    message = f"Your product '{product_name}' has been successfully registered."
    recipient_list = [user_email]
    
    return send_email_task(subject, message, recipient_list)

@shared_task
def send_daily_email_update():
    """
    Example of a periodic task that sends a daily email update
    """
    subject = "Daily Update"
    message = f"This is your daily update email sent at {datetime.now()}"
    recipient_list = ['your-test-email@example.com']  # Replace with your test email
    
    return send_email_task(subject, message, recipient_list)