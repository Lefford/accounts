from django.test import TestCase
from accounts.interface.client import ImporterClient

class TestImporter(TestCase):
    def setUp(self):
        self.base_url = 'http://api.travelbird.info'
        self.url_param = {
                          'username': 'guest@travelbird.nl',
                          'api_key': '642bbb7c573da61cc3cd3461e46eef84e8467185',
                          'format': 'json'
                          }
        
    def test_get_accounts(self):
        client = ImporterClient(self.base_url, self.url_param)
        response = client.get('api/v1account_lead/')  
        self.assertEqual(200, response.status_code)
        
    def test_resource_uri(self):
        client = ImporterClient(self.base_url, self.url_param)
        response = client.get('api/v1/account_lead/') 
        response_01 = client.get(response.content['objects'][0]['resource_uri'])
        self.assertEqual(200, response_01.status_code)
