from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import UserManager
from django.utils import timezone
from django.conf import settings

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=200, unique=True)
    phone_number = models.CharField(max_length=11, unique=True)
    username = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'username']

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin

class OtpCode(models.Model):
    email = models.EmailField(max_length=200, unique=True)
    code = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)

    def can_resend(self):
        return timezone.now() > self.created + timezone.timedelta(seconds=30)

    def __str__(self):
        return f'{self.email} - {self.code} - {self.created}'

def user_directory_path(instance, filename):
    return f'profile_pic/{instance.user.id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveSmallIntegerField(default=0)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)

    def get_image_url(self):
        if self.image:
            return self.image.url
        return settings.STATIC_URL + 'accounts/images/default.jpeg'

    def __str__(self):
        return self.user.username

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address = models.TextField(null=True, blank=True)
    postal_code = models.CharField(max_length=25, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.address} - {self.postal_code}'
