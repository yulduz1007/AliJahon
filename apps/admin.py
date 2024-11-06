from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.models import District, Region, Category, Product, AdminSite

# Register your models here.
admin.site.register(District)
admin.site.register(Region)


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    exclude = 'slug',


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    exclude = 'slug',


@admin.register(AdminSite)
class AdminSite(ModelAdmin):
    pass


