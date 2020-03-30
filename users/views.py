from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Profile, CustomUser
from .forms import ProfileUpdateForm, CustomUserChangeForm
from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from allauth.account.admin import EmailAddress
from allauth.account.utils import send_email_confirmation
from django.contrib import messages

# Create your views here.

@login_required
def profile(request):
    if request.method == "POST":
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            profile_instance = profile_form.save(commit=False)
            profile_instance.save()
            user_form.save()
            return redirect('profile')
    else:
        profile_form = ProfileUpdateForm()
        user_form = CustomUserChangeForm( initial=model_to_dict(request.user))
        profile = Profile.objects.get(user=request.user)
        verified = EmailAddress.objects.filter(user=request.user, verified=True).exists()

        return render(request, 'recipes/profile.html', {"profile": profile, "profile_form":profile_form, "user_form": user_form, 'verified':verified})


@login_required
def manual_send_verification(request):
    send_email_confirmation(request, request.user, False)
    print('Verification View')
    return redirect('profile')