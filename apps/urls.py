

from django.urls import path
from .views import get_districts, ProfileFormView, ChangePasswordFormView
from apps.views import HomeTemplateView, AuthFormView, UseDocumentTemplateView, CustomLogoutView

urlpatterns = [
    path('', HomeTemplateView.as_view(), name='home'),
    path('auth', AuthFormView.as_view(), name='auth'),
    path('doc', UseDocumentTemplateView.as_view(), name='doc'),
    path('logout', CustomLogoutView.as_view(), name='logout'),
    path('profile/edit', ProfileFormView.as_view(), name='profile-edit'),
    path('get-districts', get_districts, name='get_districts'),
    path('change-password', ChangePasswordFormView.as_view(), name='change-password'),
]