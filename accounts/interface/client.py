from restclient.clients.jsonclient import JSONClient
from accounts.utils.utils import url_join

class ImporterClient(JSONClient):
    
    def __init__(self, base_url):
        self.base_url = base_url
        
    def request(self, uri, method='GET', body=None, headers=None, redirections=5, connection_type=None):
        if not uri.startswith(self.base_url):
            uri = url_join(self.base_url, uri)
        JSONClient.request(self, uri, method=method, body=body, headers=headers, redirections=redirections, connection_type=connection_type)

    
        
    
        
        