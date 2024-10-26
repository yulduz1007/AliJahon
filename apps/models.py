from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import CharField, Model, ForeignKey, CASCADE, BigIntegerField, TextField, BooleanField, \
    OneToOneField, SET_NULL, ImageField

from django.apps import apps
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.contenttypes.models import ContentType


# Create your models here.
class CustomUserManager(UserManager):
    def _create_user(self, phone_number, email, password, **extra_fields):
        if not phone_number:
            raise ValueError("The given phone_number must be set")
        email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        phone_number = GlobalUserModel.normalize_username(phone_number)
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, email, password, **extra_fields)

    def create_superuser(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, email, password, **extra_fields)


class User(AbstractUser):
    phone_number = CharField(max_length=9, unique=True, blank=True)
    address = CharField(max_length=255, null=True, blank=True)
    telegram_id = BigIntegerField(null=True, blank=True)
    description = TextField(null=True, blank=True)
    objects = CustomUserManager()
    USERNAME_FIELD = "phone_number"
    district = ForeignKey('apps.District', SET_NULL, null=True, blank=True, unique=True)
    username = None
    is_doc_read = BooleanField(default=False, blank=True)
    image = ImageField(upload_to='users/')


class Region(Model):
    name = CharField(max_length=50)


class District(Model):
    name = CharField(max_length=50)
    region = ForeignKey('apps.Region', CASCADE, related_name='districts')
