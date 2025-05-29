from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.utils.timezone import now
from datetime import timedelta

signer = TimestampSigner()

def generate_verification_token(user):
    return signer.sign(user.email)

def verify_token(token, max_age=86400):  # 24 hours
    try:
        email = signer.unsign(token, max_age=max_age)
        return email
    except (BadSignature, SignatureExpired):
        return None

def send_verification_email(user):
    # ✅ Generate the token
    token = user.generate_email_verification_token()  
    verification_url = f"{settings.FRONTEND_URL}/api/auth/verify-email/?token={token}"

    # ✅ Debugging prints (Check if token is generated)
    print("🔹 DEBUG: Sending Verification Email")
    print(f"📧 Email: {user.email}")
    print(f"🔗 Verification URL: {verification_url}")
    print(f"🔑 Token: {token}")

    subject = "Verify Your Email"
    message = f"Click the link to verify your email: {verification_url}"

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def generate_password_reset_token(user):
    return signer.sign(f"{user.email}")

def send_password_reset_email(user):
    token = generate_password_reset_token(user)
    reset_url = f"{settings.FRONTEND_URL}/api/auth/reset-password-confirm/?token={token}"


    subject = "Reset Your Password"
    message = f"Click the link to reset your password: {reset_url}"
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def verify_password_reset_token(token, max_age=3600):  # 1-hour expiration
    try:
        email = signer.unsign(token, max_age=max_age)
        print(f"🔍 Extracted email: {email}")  # ✅ Debugging line
        return email.lower().strip()  # ✅ Ensure email is properly formatted
    except (BadSignature, SignatureExpired) as e:
        print(f"❌ Token error: {str(e)}")  # ✅ Debugging print
        return None


def send_otp_email(user_email, otp_code):
    """
    Send OTP to user's email
    Args:
        user_email (str): The recipient's email address
        otp_code (str): The OTP code to send
    """
    subject = "Your FocusReader Verification Code"
    message = f"Your OTP code is: {otp_code}\nValid for 5 minutes."
    from_email = settings.DEFAULT_FROM_EMAIL
    
    send_mail(
        subject,
        message,
        from_email,
        [user_email],
        fail_silently=False
    )
    print(f"📨 OTP sent to {user_email}")  # Debugging