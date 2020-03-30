"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from recipes.views import home, logoutview, category, dish, add_to_cart, add_in_cart, remove_from_cart, cart, add_order_info, add_billing_info, review_order, order_complete, orders, contact_us, contact_us_post_order, message_sent
from users.views import profile, manual_send_verification
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('profile/', profile, name='profile' ),
    path('verify/', manual_send_verification, name='manual_send_verification' ),
    path('logout/', logoutview, name='logout'),
    path('contact-us/', contact_us, name='contact'),
    path('message_sent/', message_sent , name='message_sent'),
    path('category/<slug:category_slug>/', category, name='category'),
    path('add_to_cart/<slug:dish_slug>/', add_to_cart, name='add_to_cart' ),
    path('creation/<slug:category_slug>/<slug:dish_slug>/', dish, name='dishx'),
    path('creation/<slug:category_slug>/<slug:dish_slug>/<int:openpics>/', dish, name='dish'),
    path('cart/', cart, name='cart'),
    path('add_order_info/<int:pk>/', add_order_info, name='add_order_info'),
    path('add_billing_info/<int:pk>/', add_billing_info, name='add_billing_info'),
    path('review_order/<int:pk>/', review_order, name='review_order'),
    path('order_complete/<int:pk>/', order_complete, name='order_complete'),
    path('orders/',orders, name='orders'),
    path('cart/<slug:dish_slug>/', add_in_cart, name='add_in_cart' ),
    path('message-after/<int:pk>/', contact_us_post_order, name='contactafterorder'),
    path('remove_from_cart/<slug:dish_slug>/<int:pk>/', remove_from_cart, name='remove_from_cart' ),
    path('accounts/', include('allauth.urls')),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)