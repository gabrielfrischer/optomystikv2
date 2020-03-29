from django.db.models.signals import post_save
from allauth.account.signals import user_signed_up
from .models import CustomUser, Profile
from django.dispatch import receiver
from django.core.mail import send_mail


@receiver(user_signed_up)
def create_profile(sender, **kwargs):
    print("Signal is being fired***********************************************************8")
    user = kwargs['user']
    Profile.objects.get_or_create(user=user)

