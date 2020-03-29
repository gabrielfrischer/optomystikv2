from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.

# class Role(models.Model):
#     ROLE_CHOICES = (
#       ('salesman', 'salesman'),
#       ('supervisor', 'supervisor'),
#       ('technician', 'technician'),
#   )

#     user_type = models.CharField(choices=ROLE_CHOICES, default='technician', max_length=20)


class CustomUser(AbstractUser):
    #role = models.OneToOneField(Role, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    def __str__(self):
        return f'{self.first_name} {self.last_name}'



class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(default='defaultprofileimage.png', upload_to='profile_pictures')