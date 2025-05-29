from django.core.mail import send_mail
from firebase_admin import messaging

def send_push_notification(user, message):
    """
    Sends a push notification to the user's device.
    """
    if not user.device_token:
        return  # ✅ Skip if user has no push notification token

    message = messaging.Message(
        notification=messaging.Notification(
            title="New Achievement!",
            body=message,
        ),
        token=user.device_token,
    )

    response = messaging.send(message)
    return response


def send_email_notification(email, subject, message):
    """
    Sends an email notification to the user.
    """
    send_mail(
        subject=subject,
        message=message,
        from_email="no-reply@focusread.com",
        recipient_list=[email],
        fail_silently=True,
    )
