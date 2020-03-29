from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Profile
from django.contrib.auth.admin import UserAdmin


# class RoleInline(admin.StackedInline):
#     model = Role
#     fields = ('user_type',)


class UserProfileInline(admin.StackedInline):
    model = Profile


class CustomUserAdmin(AuthUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    inlines=[UserProfileInline]
    list_display = ['email','first_name', 'last_name',]


admin.site.register(CustomUser, CustomUserAdmin)
