from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView
from django.http import JsonResponse
from .models import District
from apps.forms import AuthForm, ProfileForm, ChangePasswordForm
from apps.models import User, Region


# Create your views here.
class HomeTemplateView(TemplateView):
    template_name = "apps/home.html"


class AuthFormView(FormView):
    form_class = AuthForm
    template_name = "apps/user/auth.html"
    success_url = reverse_lazy('profile-edit')

    def form_valid(self, form):
        clean_data = form.cleaned_data
        user: User = User.objects.filter(phone_number=clean_data.get("phone_number")).first()
        if not user:
            clean_data['password'] = make_password(clean_data.get("password"))
            user, is_create = User.objects.get_or_create(**clean_data)
            login(self.request, user)
            return super().form_valid(form)

        else:
            is_equal = check_password(clean_data.get("password"), user.password)
            if is_equal:
                login(self.request, user)
                return super().form_valid(form)
            else:
                messages.error(self.request, "Password is not Match !")
                return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, "\n".join([i[0] for i in form.errors.values()]))
        return super().form_invalid(form)


class ChangePasswordFormView(FormView):
    form_class = ChangePasswordForm
    template_name = "apps/user/profile.html"
    success_url = reverse_lazy('profile-edit')

    def form_valid(self, form):
        user = self.request.user
        password = form.cleaned_data.get("password")
        new_password = form.cleaned_data.get("new_password")
        if not check_password(password, user.password):
            messages.error(self.request, "Old password is incorrect !")
            return super().form_valid(form)
        user: User = User.objects.filter(pk=user.pk).first()
        user.password = new_password
        user.save()
        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form)


class ProfileFormView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy("auth")
    form_class = ProfileForm
    template_name = "apps/user/profile.html"
    success_url = reverse_lazy('profile-edit')

    def get_context_data(self, **kwargs):
        user: User = self.request.user
        data = super().get_context_data(**kwargs)
        if user.district:
            district = District.objects.filter(pk=user.district.pk).first()
            data['district_region'] = district.region.pk
            data['district'] = district

        data['regions'] = Region.objects.all()
        return data

    def form_valid(self, form):
        user = self.request.user
        district_id = form.cleaned_data.get('district')
        if district_id == "0":
            del form.cleaned_data['district']
        User.objects.filter(pk=user.pk).update(**form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)


class UseDocumentTemplateView(TemplateView):
    template_name = 'apps/document.html'


class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(self.request)
        return redirect('home')


def get_districts(request):
    region_id = request.GET.get('region_id')
    if region_id:
        districts = District.objects.filter(region_id=region_id).values("id", "name")
        return JsonResponse(list(districts), safe=False)
    return JsonResponse({'error': 'No region selected'}, status=400)
