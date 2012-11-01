from django.db import models

class Account(models.Model):
    resource_uri = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birth_date = models.DateField()
    gender = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    street_name = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    lead = models.BooleanField()
    mailing_list = models.CharField(max_length=200)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    tr_referral = models.CharField(max_length=255)
    utm_medium = models.CharField(max_length=255)
    utm_source = models.CharField(max_length=255)
    
    def __unicode__(self):
        return u' '.join([self.first_name, self.last_name])
