from django.contrib.auth.models import AbstractUser, UserManager
from django.apps import apps
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django_resized import ResizedImageField
from django.db.models import (CharField,
                              Model,
                              ForeignKey,
                              CASCADE,
                              BigIntegerField,
                              TextField,
                              BooleanField,
                              SET_NULL,
                              ImageField,
                              PositiveIntegerField,
                              SlugField,
                              OneToOneField,
                              DecimalField,
                              TextChoices,
                              DateTimeField)


# Create your models here.
class DateTimeBaseModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseSlug(Model):
    name = CharField(max_length=255)
    slug = SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique = self.slug
            num = 1
            while Category.objects.filter(slug=unique).exists():
                unique = f'{self.slug}-{num}'
                num += 1
            self.slug = unique
        return super().save(*args, **kwargs)


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
    district = OneToOneField('apps.District', SET_NULL, null=True, blank=True)
    username = None
    is_doc_read = BooleanField(default=False, blank=True)
    image = ImageField(upload_to='users/')
    balance = DecimalField(max_digits=12, decimal_places=0, default=0)

    @property
    def self_wishlist(self):
        return self.wishlists.all().values_list('product_id', flat=True)


class Region(Model):
    name = CharField(max_length=50)


class District(Model):
    name = CharField(max_length=50)
    region = ForeignKey('apps.Region', CASCADE, related_name='districts')


class Category(BaseSlug):
    icon = ImageField(upload_to='categories/')

    def __str__(self):
        return self.name


class Product(BaseSlug, DateTimeBaseModel):
    image = ResizedImageField(size=[200, 200], quality=100, upload_to='products/')
    description = TextField()
    quantity = PositiveIntegerField(default=1)
    discount = DecimalField(max_digits=6, decimal_places=2)
    price = DecimalField(max_digits=12, decimal_places=2)
    salesman_price = DecimalField(max_digits=12, decimal_places=2)
    category = ForeignKey('apps.Category', CASCADE, to_field='slug', related_name='products')

    @property
    def discount_price(self):
        return self.price * (100 - self.discount) / 100

    def __str__(self):
        return self.name


class Order(DateTimeBaseModel):
    class StatusType(TextChoices):
        NEW = "new", 'New'
        READY = "ready", 'Ready'
        DELIVER = "deliver", 'Deliver'
        DELIVERED = "delivered", 'Delivered'
        CANCEL_CALL = "cancel_call", 'Cancel_call'
        CANCELED = "canceled", 'Canceled'
        COMPLETED = "completed", 'Completed'
        ARCHIVED = 'archived', 'Archived'

    product = ForeignKey('apps.Product', CASCADE, to_field='slug', related_name='orders')
    quantity = PositiveIntegerField(default=1)
    status = CharField(max_length=50, choices=StatusType.choices, default=StatusType.NEW)
    thread = ForeignKey('apps.Thread', SET_NULL, null=True, blank=True, related_name="orders")
    phone_number = CharField(max_length=50)
    name = CharField(max_length=50)
    district = ForeignKey('apps.District', SET_NULL, null=True, blank=True, related_name='orders')
    address = CharField(max_length=255)
    all_amount = DecimalField(max_digits=9, decimal_places=2)
    user = ForeignKey('apps.User', CASCADE, related_name='orders')


class Thread(DateTimeBaseModel):
    owner = ForeignKey('apps.User', CASCADE, related_name='threads')
    product = ForeignKey('apps.Product', CASCADE, related_name='threads')
    title = CharField(max_length=100)
    discount_price = DecimalField(max_digits=9, decimal_places=0, default=0)
    visit_count = DecimalField(max_digits=9, decimal_places=0, default=0)


class AdminSite(Model):
    delivery_price = DecimalField(max_digits=9, decimal_places=1)
    competition_photo = ImageField(upload_to="site_settings")


class WishList(Model):
    user = ForeignKey('apps.User', CASCADE, related_name='wishlists')
    product = ForeignKey('apps.Product', CASCADE, related_name='wishlists')
