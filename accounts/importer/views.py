import json
from django.views.generic import ListView
from accounts.importer.models import Account
from django.views.generic.base import View
from django.http import HttpResponse
from accounts.importer.forms import AccountForm
from django.core.cache import cache
from django.forms.models import model_to_dict
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
import datetime


class AccountList(ListView):
    
    model = Account
    
    def get_context_data(self, **kwargs):
        context = super(AccountList, self).get_context_data(**kwargs)
        context.update({'account_form': AccountForm()})
        # get remote data
        return context
    
class JSONResponseMixin(object):

    response_class = HttpResponse

    def render_to_response(self, context=[], **kwargs):
        kwargs["content_type"] = "application/json"
        return JSONResponseMixin.response_class(self.convert_to_json(context), **kwargs)

    def convert_to_json(self, context):
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else ''
        return json.dumps(context, default=dthandler)
    
class CreateAccount(JSONResponseMixin, FormView):
    
    success_url = reverse_lazy('search_account', kwargs={'website': 'example'})
    
    form_class = AccountForm
    
    def form_valid(self, form):
        form.save()
        if self.request.is_ajax():
            return JSONResponseMixin.render_to_response(self)
        return super(CreateAccount, self).form_valid(form)

class AccountLookup(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):
        result= dict()
        q = request.GET.get("q")
        if q:
            city_list = cache.get(u"account_list")
            if not city_list:
                account_list = dict()
                cache.set(u"account_list", city_list)
            cache_result = account_list.get(q)
            if not cache_result:
                account_list[q] = Account.objects.filter(first_name__startswith=q)
                cache_result = account_list[q]
            convert_result = [model_to_dict(account) for account in cache_result]
            result = {
                "account_set": convert_result
            }
        return JSONResponseMixin.render_to_response(self, context=result)