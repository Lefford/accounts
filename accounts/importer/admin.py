from django.contrib import admin
from accounts.importer.models import FlightTicket, Hotel

class FlightTicketAdmin(admin.ModelAdmin):
    pass

class HotelAdmin(admin.ModelAdmin):
    pass

admin.site.register(FlightTicket, FlightTicketAdmin)
admin.site.register(Hotel, HotelAdmin)
