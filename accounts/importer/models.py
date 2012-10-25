from django.db import models
from accounts.account.models import Company

class Resource(models.Model):
    class Meta:
        abstract = True
        
    partner = models.ForeignKey(Company)
    resource_type = models.CharField(max_length=255)

class FlightTicket(Resource):
    pass

class Hotel(Resource):
    pass
