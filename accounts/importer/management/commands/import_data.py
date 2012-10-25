from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model
from accounts.interface.client import ImporterClient
from accounts.account.models import Company, AccountConfiguration

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        if len(args) == 0:
            raise CommandError('Company and resource name required')
        
        company = None
        try:
            company = Company.objects.get(name=args[0])
        except Company.DoesNotExist, e:
            raise CommandError('{0} is a unknown company'.format(company))
        
        account = None
        if company:
            try:
                account = AccountConfiguration.objects.get(company=company)
            except AccountConfiguration.DoesNotExist, e:
                raise CommandError('{0} has no account configuration'.format(args[0]))
            
        if account:
            client = ImporterClient(account.base.url)
            response = None
            try:
                headers = dict()
                headers.update({'user name': account.user_name, 'api_key': account.api_key})
                response = client.get(args[1])
            except ValueError, e:
                raise CommandError('Error code {0} for fetching {1}'.format(e, args[1]))
            
            content = response.content if response else list()
            model = get_model(args[1])
            for resource in content:
                    resource# save resource in db
