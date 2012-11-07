from django.conf.urls import patterns, url
from accounts.importer import views

urlpatterns = patterns('',
    url(r'(?P<website>[\w-]+)/account$', views.AccountList.as_view()),
    url(r'(?P<website>[\w-]+)/search-account$', views.AccountLookup.as_view(), name="search_account"),
    url(r'(?P<website>[\w-]+)/account/add$', views.CreateAccount.as_view(), name="add_account"),
)
