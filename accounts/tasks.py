from celery import shared_task
from accounts.models import OtpCode
from datetime import timedelta
from django.utils import timezone

@shared_task
def remove_expired_otp_codes():
    expired_time = timezone.now() - timedelta(minutes=2)
    deleted_count, _ = OtpCode.objects.filter(created__lt=expired_time).delete()
    print(f'deleted {deleted_count} expired OTP codes')
