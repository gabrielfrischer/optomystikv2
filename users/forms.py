from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm

from .models import CustomUser, Profile



class CustomUserCreationForm(SignupForm):

    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    alternative_identity = forms.CharField(max_length=50, label='Alternative Identity')

    def save(self, request):

        # Ensure you call the parent classes save.
        # .save() returns a User object.
        user = super(CustomUserCreationForm, self).save(request)

        # Add your own processing here.
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.alternative_identity = self.cleaned_data['alternative_identity']
        user.save()
        # You must return the original result.
        return user

class CustomUserChangeForm(UserChangeForm):
    password = None
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'alternative_identity', 'email',)



class ProfileUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ["profile_picture"]
