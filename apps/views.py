from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView, ListView, DetailView
from django.http import JsonResponse, request
from .models import District, Product, WishList, Category, AdminSite, Order, Thread
from apps.forms import AuthForm, ProfileForm, ChangePasswordForm, OrderForm, ThreadForm
from apps.models import User, Region


# Create your views here.
class HomeListView(ListView):
    template_name = "apps/home.html"
    queryset = Category.objects.all()
    context_object_name = "categories"

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        data['products'] = Product.objects.all()
        return data


class ProductDetailFormView(ListView, FormView):
    queryset = Product.objects.all()
    context_object_name = "product"
    form_class = OrderForm
    template_name = "apps/site/product-detail.html"

    def get_queryset(self):
        query = super().get_queryset()
        thread_id = self.kwargs.get('thread_id')
        if thread_id:
            thread = Thread.objects.filter(id=thread_id).first()
            thread.visit_count += 1
            thread.save()
            product = thread.product
            query = query.filter(id=product.id).first()
        else:
            slug = self.kwargs.get("slug")
            query = query.filter(slug=slug).first()
        return query

    def get_context_data(self,  **kwargs):
        context = super().get_context_data( **kwargs)
        thread_id = self.kwargs.get('thread_id')
        context['all_amount'] = context['product'].discount_price
        if thread_id:
            context['thread'] = Thread.objects.filter(id=thread_id).first()
            context['all_amount'] = context['product'].discount_price - context['thread'].discount_price
        context['site'] = AdminSite.objects.all().first()
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        site = AdminSite.objects.all().first()
        product = Product.objects.filter(slug=data.get("product")).first()
        product.quantity -= 1
        product.save()
        all_amount = site.delivery_price + product.discount_price
        if data.get("thread"):
             thread = Thread.objects.filter(id=data.get("thread")).first()
             data['thread'] = thread
             all_amount -= thread.discount_price
        else:
            del data['thread']
        data['product'] = product
        data['user'] = self.request.user
        obj, created = Order.objects.get_or_create(**data, all_amount=all_amount)
        context = {
            "order": obj,
            "site": site,
            "product_price": product.discount_price
        }
        if data.get("thread"):
            context['product_price'] = product.discount_price - data.get("thread").discount_price
        return render(self.request, 'apps/site/order-success.html', context)


class OrderSuccessTemplateView(TemplateView):
    template_name = "apps/site/order-success.html"


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
        messages.success(self.request, "Password is changed successfully !")
        user: User = User.objects.filter(pk=user.pk).first()
        user.password = new_password
        user.save()
        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "\n".join([i[0] for i in form.errors.values()]))
        return super().form_invalid(form)


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


class UseDocumentTemplateView(TemplateView):
    template_name = 'apps/document.html'


class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(self.request)
        return redirect('home')


def wishlist_view(request):
    if request.POST:
        user = request.user
        if not user:
            return redirect('auth')
        product_id = request.POST.get('product_id')
        obj, created = WishList.objects.get_or_create(user=user, product_id=product_id)
        if not created:
            obj.delete()
        return JsonResponse({"response": created})
    else:
        context = {
            "wishlists": request.user.wishlists.all()
        }
        return render(request, "apps/user/wishlist.html", context)


def get_districts(request):
    region_id = request.GET.get('region_id')
    if region_id:
        districts = District.objects.filter(region_id=region_id).values("id", "name")
        return JsonResponse(list(districts), safe=False)
    return JsonResponse({'error': 'No region selected'}, status=400)


class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/site/mahsulot.html'
    context_object_name = 'products'

    def get_queryset(self):
        cat_slug = self.request.GET.get("category")
        query = super().get_queryset()
        if cat_slug:
            query = query.filter(category__slug=cat_slug)
        return query

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['categories'] = Category.objects.all()
        return data


class MarketCategoryListView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/salesman/market.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = super().get_queryset()
        slug = self.kwargs.get('slug')
        q = self.request.GET.get("q")
        if slug == 'top':
            query = query.annotate(total_sold=Sum('orders quantity')).order_by('-total_sold')
        elif slug != 'all':
            query = query.filter(category__slug=slug).all()
        elif q:
            query = query.filter(Q(name__icontains=q) | Q(description__icontains=q)).all()
        return query

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['categories'] = Category.objects.all()
        return data


class ThreadListFormView(FormView):
    form_class = ThreadForm
    template_name = "apps/salesman/thread-list.html"
    success_url = reverse_lazy('thread-list')

    def form_valid(self, form):
        data = form.cleaned_data
        if data.get("discount_price") > data.get("product").salesman_price:
            messages.error(self.request, "Chegirma narxi xato")
            return redirect("market", 'all')
        data['owner'] = self.request.user
        Thread.objects.create(**data)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['threads'] = self.request.user.threads.all()
        return context


class OrderListView(ListView):
    queryset = Order.objects.select_related('district').all()
    template_name = 'apps/site/order-list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(user=self.request.user).all()
        return query


def searchView(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query, description__icontains=query)
        data = [
            {
                "id": product.id,
                "name": product.name,
                "url": product.get_absolute_url(),
                "image_url": product.image.url if product.image else "",
                "discount_price": product.discount_price,
                "salesmen_price": product.salesmen_price,
                "quantity": product.quantity,
                "discount": product.discount > 0

            }
            for product in products
        ]
    else:
        data = []
    return JsonResponse(data, safe=False)
