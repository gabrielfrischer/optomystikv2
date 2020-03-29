from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm

from .models import CustomUser, Profile



class CustomUserCreationForm(SignupForm):

    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')



class CustomUserChangeForm(UserChangeForm):
    password = None
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email',)



class ProfileUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ["profile_picture"]
