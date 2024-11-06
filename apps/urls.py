from django.urls import path
from apps.views import (HomeListView,
                        AuthFormView,
                        UseDocumentTemplateView,
                        CustomLogoutView,
                        OrderSuccessTemplateView,
                        ProductListView,
                        wishlist_view,
                        MarketCategoryListView,
                        ThreadListFormView,
                        get_districts,
                        ProfileFormView,
                        ChangePasswordFormView,
                        ProductDetailFormView,
                        OrderListView,
                        searchView)

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('category/<str:slug>', ProductListView.as_view(), name='category'),
    path("product-detail/<str:slug>", ProductDetailFormView.as_view(), name="product_detail"),
]

urlpatterns += [
    path('sales/market/category/<str:slug>', MarketCategoryListView.as_view(), name='market'),
    path('sales/market/oqim', ThreadListFormView.as_view(), name='thread-list'),
    path('oqim/<int:thread_id>', ProductDetailFormView.as_view(), name='thread'),
    path('sales/market/search', searchView, name='search'),
]

urlpatterns += [
    path('order/list', OrderListView.as_view(), name='order-list'),
]

urlpatterns += [
    path("order-success", OrderSuccessTemplateView.as_view(), name="order_success"),
    path("user/wishlist", wishlist_view, name="wishlist"),
    path("user/wishlist", wishlist_view, name="wishlist"),
    path('auth', AuthFormView.as_view(), name='auth'),
    path('doc', UseDocumentTemplateView.as_view(), name='doc'),
    path('logout', CustomLogoutView.as_view(), name='logout'),
    path('profile/edit', ProfileFormView.as_view(), name='profile-edit'),
    path('get-districts', get_districts, name='get_districts'),
    path('change-password', ChangePasswordFormView.as_view(), name='change-password'),
]
