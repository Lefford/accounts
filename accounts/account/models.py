# model accounts
from django.db import models
from django.contrib.auth.models import User

class AccountConfiguration(models.Model):
    base_url = models.CharField(max_length=255)
    user_name = models.ForeignKey(User)
    api_key = models.CharField(max_length=255)
    
class Company(models.Model):
    name = models.CharField(max_length=255)
    
class UserProfile(models.Model):
    user = models.ForeignKey(User)
    company = models.ForeignKey(Company)
