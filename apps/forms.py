from http import HTTPStatus
import re
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms import Form, CharField, BooleanField, ModelForm
from apps.models import Thread


class AuthForm(Form):
    phone_number = CharField(required=True, max_length=20)
    password = CharField(required=True, max_length=50)
    is_doc_read = BooleanField(required=False)

    def clean_password(self):
        password = self.cleaned_data['password']
        if not len(password) >= 5:
            raise ValidationError('Password must be at least 5 characters', code=HTTPStatus.BAD_REQUEST)
        return password

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        return re.sub(r'\D', '', phone_number)[3:]


class ChangePasswordForm(Form):
    password = CharField(max_length=50)
    new_password = CharField(max_length=50)
    confirm_password = CharField(max_length=50)

    def clean(self):
        clean_data = self.cleaned_data
        new_password = clean_data.get('new_password')
        confirm_password = clean_data.get('confirm_password')
        if new_password != confirm_password:
            raise ValidationError('Passwords do not match')
        if len(new_password) < 5:
            raise ValidationError('Password must be at least 5 characters')
        del clean_data['confirm_password']
        clean_data["new_password"] = make_password(clean_data["new_password"])
        return clean_data


class ProfileForm(Form):
    first_name = CharField(required=False, max_length=50)
    last_name = CharField(required=False, max_length=50)
    district = CharField(max_length=50, required=False)
    address = CharField(required=False, max_length=50)
    telegram_id = CharField(required=False, max_length=50)
    description = CharField(required=False, max_length=50)

    def clean_telegram_id(self):
        telegram_id = self.cleaned_data.get('telegram_id')
        if not telegram_id:
            return None
        return telegram_id


class OrderForm(Form):
    name = CharField(max_length=255)
    phone_number = CharField(max_length=255)
    product = CharField(max_length=255)
    thread = CharField(max_length=255, required=False)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        return re.sub(r'\D', '', phone_number)[3:]


class ThreadForm(ModelForm):
    class Meta:
        model = Thread
        exclude = "created_at", "updated_at", "visit_count"

    def __init__(self, *args, **kwargs):
        super(ThreadForm, self).__init__(*args, **kwargs)
        self.fields['owner'].required = False
