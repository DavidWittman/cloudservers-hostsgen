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

import cloudservers

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

    cs = cloudservers.Client(sys.argv[1], sys.argv[2])
    print "Generating new server list for %s..." % sys.argv[1]
    servers = cs.get_server_list()
    write_new_hosts(servers)
