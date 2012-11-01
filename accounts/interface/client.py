import urllib

from accounts.utils.utils import url_join
from restclient.clients.jsonclient import JSONClient

class ImporterClient(JSONClient):
    
    def __init__(self, base_url=u'', url_params=None):
        self.base_url = base_url
        self.url_params = url_params
        # enable cache default is 2 hour
        super(ImporterClient, self).__init__('.cache')
        
    def request(self, uri, method='GET', body=None, headers=None, redirections=5, connection_type=None):
        if not uri.startswith(self.base_url):
            uri = url_join(self.base_url, uri)
        if self.url_params:
            uri = "?".join([uri, urllib.urlencode(self.url_params)])
        return super(ImporterClient, self).request(uri, method, body, headers, redirections, connection_type)
