from django.conf.urls import patterns, include, url
from django.contrib import admin
from accounts.api.resource import AccountResource, PersonResource

account_resource = AccountResource()
person_resource = PersonResource()

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'accounts.views.home', name='home'),
    # url(r'^accounts/', include('accounts.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^overview/', include('accounts.importer.urls')),
    url(r'^data/', include(person_resource.urls)),
)
