from django.contrib import admin
from .models import Category, Dish, DishImages, Cart, Order, OrderInfo, BillingAddress, ContactUs
from django.db import models
# Register your models here.

class InlineDishes(admin.TabularInline):
    model = Dish
    extra = 1
    exclude = ('slug',)


@admin.register(Category)
class MainCategory(admin.ModelAdmin):
    inlines = [InlineDishes,]




class InlineDishImages(admin.TabularInline):
    model = DishImages
    fields = ['dish', 'image', 'image_thumb',]
    readonly_fields = ('image_thumb',)
    exclude = ('slug',)
    extra = 1

@admin.register(Dish)
class MainDishes(admin.ModelAdmin):
    inlines=[InlineDishImages,]
    exclude=('slug',)


admin.site.register(Cart)
admin.site.register(Order)
admin.site.unregister(Order)


class InlineOrderInfo(admin.StackedInline):
    model = OrderInfo

class InlineBillingInfo(admin.StackedInline):
    model = BillingAddress

class InlineOrderMessages(admin.TabularInline):
    model = ContactUs

@admin.register(Order)
class MainOrders(admin.ModelAdmin):
    list_display = ('id',)
    inlines = [InlineOrderInfo, InlineBillingInfo, InlineOrderMessages]


admin.site.register(ContactUs)