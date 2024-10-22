from django.contrib.auth.models import AbstractUser
from django.db import models  # all methods and fields of normal user models


# Create your models here.
# Inheriting all functionality of normal user model for utilization in our user model 'Account' personal userModel allows for greater flexibility, additional fields, 3rd party integrations etc.This is referenced at end of settings.py
# By defining our own usermodel we now have complete control over the fields and methods of the model allowing us to customize based on our needs.
class Account(AbstractUser):
    pass
