import os

from tastypie.resources import ModelResource
from accounts.importer.models import Account, Person
from django.conf.urls import url
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import BasicAuthentication

class CommonResource(ModelResource):
    
    LIST_VIEW_FIELDS = ('api_url',)
    DETAIL_VIEW_FIELDS = ('id', 'resource_uri', 'api_url')
    
    def fields_list_view(self):
        return self.LIST_VIEW_FIELDS
    
    def fields_detail_view(self):
        return self.DETAIL_VIEW_FIELDS
    
    def alter_list_data_to_serialize(self, request, data):
        if isinstance(data['meta'], dict):
            del(data['meta'])
            
        data['_'.join([self._meta.resource_name, 'set'])] = data['objects']
        del(data['objects'])
        
        return data

    def alter_deserialized_list_data(self, request, data):
        data['objects'] = data['_'.join([self._meta.resource_name, 'set'])]
        del data['_'.join([self._meta.resource_name, 'set'])]
        return data
    
    def dehydrate(self, bundle):
        """
        Adding fields and determine which fields are visible for a particular view
        """
        
        META = bundle.request.META.copy()
        bundle.data['api_url'] = os.path.join(
                                              ''.join([META['SERVER_PROTOCOL'].split("/")[0].lower(), ':', '//']),
                                              ':'.join([META['SERVER_NAME'], META['SERVER_PORT']]),
                                              self.get_resource_uri(bundle)[1:]
                                              )
        
        request = bundle.request
        field_list = bundle.data.copy()
        if request.META['PATH_INFO'] == self.get_resource_uri(bundle):
            #/data/{resource}/{id}
            for f in bundle.data:
                fields_detail_view = self.fields_detail_view()
                if f in fields_detail_view:
                    del field_list[f]
        elif request.META['PATH_INFO'] == os.path.join('/', request.META['PATH_INFO'][1:].split('/')[0], self._meta.resource_name):
            #/data/{resource}
            for f in bundle.data:
                fields_list_view = self.fields_list_view()
                if f not in fields_list_view:
                    del field_list[f]
        bundle.data = field_list
        
        return bundle
    
    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        # Due to the way Django parses URLs, ``get_multiple`` won't work without
        # a trailing slash.
        # removed trailing slash for resource
        return [
            url(r"^(?P<resource_name>%s)$" % (self._meta.resource_name), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/schema$" % (self._meta.resource_name), self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^(?P<resource_name>%s)/set/(?P<pk_list>\w[\w/;-]*)/$" % self._meta.resource_name, self.wrap_view('get_multiple'), name="api_get_multiple"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)$" % (self._meta.resource_name), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
    
class AccountResource(ModelResource):
    
    class Meta:
        queryset = Account.objects.all()
        fields =['first_name',]
        resource_name = 'account_lead'
        allowed_methods = ['get', 'post']
    
class PersonResource(CommonResource):
    
    class Meta:
        queryset = Person.objects.all()
        resource_name = 'person'
        list_allowed_methods = ['get', 'post', 'put']
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
        
    def fields_list_view(self):
        list_view_fields = super(PersonResource, self).fields_list_view()
        list_view_fields = list(list_view_fields)
        list_view_fields.append('first_name')
        return list_view_fields
    