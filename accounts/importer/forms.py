from django import forms
from accounts.importer.models import Account

class AccountForm(forms.ModelForm):
    
    class Meta:
        model = Account 
        widgets = {
                   'mailing_list': forms.SelectMultiple(),
                   }