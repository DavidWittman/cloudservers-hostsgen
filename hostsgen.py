#!/usr/bin/env python
"""
CloudServers /etc/hosts Generator
Author: David Wittman <david@wittman.com>
Date: Oct 11, 2011
	
Auto-populates the system's hosts file with private IP addresses
of Rackspace Cloud Servers on the account specified by the arguments
<user> and <apikey>. Much of the API connection code has been reused 
from the existing Python CloudServers API.

"""

import fcntl
import os
import sys
import socket
import struct

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

class CloudServersClient(httplib2.Http):
    """Client for interfacing with the Rackspace Cloud Servers API

    Args:
        user: String containing the Rackspace Cloud username
        apikey: String containing Rackspace Cloud API Key

    >>> cs = CloudServersClient('user','acbd18db4cc2f85cedef654fccc4a4d8')
    
    """

    API_URL = 'https://auth.api.rackspacecloud.com/v1.0'
    
    def __init__(self, user, apikey):
        super(CloudServersClient, self).__init__()
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
            for server in body['servers']:
                servers[server['name']] = server['addresses']['private'][0]
        else:
            servers = None

        return servers

    def _cs_request(self, url, method, **kwargs):
        if not self.mgmt_url:
            self.authenticate()

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
        (resp, content) = super(CloudServersClient, self).request(*args, **kwargs)
        if content:
            json.loads(content)
        else:
            content = None
        if resp.status in (400, 401, 403, 404, 413, 500):
            raise Exception

        return resp, content

def write_new_hosts(servers):
    """Writes new Cloud Servers to the hosts file.
    
    Args:
        servers: A dictionary of the servers (key) and 
            their IP address (value).

    >>> write_new_hosts({'web01':'10.180.1.42'})
    
    """

    def get_local_ip(interface):
        """Retrieves IP address from an interface in Linux
        Adopted from http://goo.gl/otHJG

        Args:
            interface: String representing the local interface
                to get the IP address for.
        Returns:
            The IP address of interface

        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,	# SIOCGIFADDR
            struct.pack('256s', interface[:15])
        )[20:24])

    sys.stdout.write("Writing new entries to hosts file... ")
    try:
        hf = open('/etc/hosts', 'r+')
        hosts = hf.read()
        # Make sure we don't add an entry for this server
        try:
            hosts += get_local_ip('eth1')
        except:
            print "[Error] Unable to retrieve local IP address for eth1."
	    	
        hf.write('\n')
        for (name, ip) in servers.items():
            if ip in hosts:
                continue
            hf.write(ip + '\t' + name + '\n')
        hf.close()
        print "Done!"
    except IOError, e:
        print e

def is_root():
    """Make sure the script is running as root"""
    if os.geteuid() != 0:
        print "Y U NO ROOT?"
        raise SystemExit(1)

def usage():
    print "Usage:\t%s <user> <apikey>" % sys.argv[0]

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv[2]) != 32:
        usage()
        raise SystemExit(1)
    is_root()

    cs = CloudServersClient(sys.argv[1], sys.argv[2])
    print "Generating new server list for %s..." % sys.argv[1]
    servers = cs.get_server_list()
    write_new_hosts(servers)
