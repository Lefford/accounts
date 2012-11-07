from django.conf.urls import patterns, url
from accounts.importer import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'accounts.views.home', name='home'),
    # url(r'^accounts/', include('accounts.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'(?P<website>[\w-]+)/account$', views.AccountList.as_view()),
    url(r'(?P<website>[\w-]+)/search-account$', views.AccountLookup.as_view(), name="search_account"),
    url(r'(?P<website>[\w-]+)/account/add$', views.CreateAccount.as_view(), name="add_account"),
)
