from django.db import models

class Account(models.Model):
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(blank=True)
    gender = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    street_name = models.CharField(max_length=255, blank=True)
    zipcode = models.CharField(max_length=255, blank=True)
    lead = models.BooleanField()
    mailing_list = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    tr_referral = models.CharField(max_length=255, blank=True)
    utm_medium = models.CharField(max_length=255, blank=True)
    utm_source = models.CharField(max_length=255, blank=True)
    
    def __unicode__(self):
        return u' '.join([self.first_name, self.last_name])
    
class Person(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return ' '.join([self.first_name, self.last_name])
