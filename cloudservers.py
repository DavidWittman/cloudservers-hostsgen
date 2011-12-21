#!/usr/bin/env python

try:
    import json
except ImportError, e:
    try:
        import simplejson as json
    except ImportError, e:
        print "[Error] This script requires the package python-simplejson."
        raise SystemExit(1)
try:
    import httplib2
except ImportError, e:
    print "[Error] This script requires the package python-httplib2."
    raise SystemExit(1)

class ApiError(Exception):
    pass

class Client(httplib2.Http):
    """Client for interfacing with the Rackspace Cloud Servers API

    Args:
        user: String containing the Rackspace Cloud username
        apikey: String containing Rackspace Cloud API Key

    >>> cs = Client('user','acbd18db4cc2f85cedef654fccc4a4d8')
    
    """

    API_URL = 'https://auth.api.rackspacecloud.com/v1.0'
    
    def __init__(self, user, apikey):
        super(Client, self).__init__()
        self.API_USER = user
        self.API_KEY = apikey
        self.auth_token = None
        self.mgmt_url = None

    def authenticate(self):
        """Authenticate with the Rackspace Cloud API"""

        headers = { 'X-Auth-User': self.API_USER,
                    'X-Auth-Key': self.API_KEY }

        (resp, content) = self.request(self.API_URL, 'GET', headers=headers)

        self.mgmt_url = resp['x-server-management-url']
        self.auth_token = resp['x-auth-token']
        
    def get_server_list(self, **kwargs):
        """Gets a list of servers on the account

        Args:
            kwargs: A dictionary of headers to pass with the API request
        Returns:
            A dictionary containing the server name and private IP

        """

        servers = {}
        (resp, body) = self._cs_request('/servers/detail', 'GET', **kwargs)
        if body:
            body = json.loads(body)
            serverlist = [(s['name'], s['addresses']) for s in body['servers']]
            for (name, addr) in serverlist:
                servers.setdefault(name, addr)
        else:
            servers = None

        return servers

    def _cs_request(self, url, method, **kwargs):
        if not self.mgmt_url:
            try:
                self.authenticate()
            except ApiError:
                print "[Error] Error authenticating with Rackspace Cloud API"
                raise SystemExit(1)

        try:
            kwargs.setdefault('headers', {})['X-Auth-Token'] = self.auth_token
            (resp, content) = self.request(self.mgmt_url + url, method, **kwargs)
            return resp, content
        except Exception, e:
            try:
                self.authenticate()
                resp, content = self.request(self.mgmt_url + url, method, **kwargs)
                return resp, content
            except Exception:
                print e

    def request(self, *args, **kwargs):
        kwargs.setdefault('headers', {})
        (resp, content) = super(Client, self).request(*args, **kwargs)
        if resp.status in (400, 401, 403, 404, 413, 500):
            raise ApiError
        if content:
            json.loads(content)
        else:
            content = None

        return resp, content
