from django.contrib.auth.models import AbstractUser
from allauth.account.forms import SignupForm
from django.db import models


class CustomUser(AbstractUser):
    #role = models.OneToOneField(Role, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    alternative_identity = models.CharField(max_length=50)
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'



class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(default='defaultprofileimage.png', upload_to='profile_pictures')