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
from optparse import OptionParser

import cloudservers

def write_new_hosts(servers, opts):
    """Writes new Cloud Servers to the hosts file.
    
    Args:
        servers: A dictionary of the servers (key) and 
            their IP address (value).

    >>> write_new_hosts({'web01':'10.180.1.42'})
    
    """
    sys.stdout.write("Writing new entries to hosts file... ")
    try:
        hf = open('/etc/hosts', 'r+')
        hosts = hf.read()
        # Make sure we don't add an entry for this server
        try:
            hosts += get_local_ip('eth1')
        except:
            sys.stderr.write("[Warning] Unable to retrieve local IP address for eth1\n")
	    
        ip_type = opts.public is True and "public" or "private"
        servers = [(k, v[ip_type][0]) for (k,v) in servers.items()]
        hf.write('\n')
        for (name, ip) in servers:
            if ip in hosts:
                continue
            hf.write(ip + '\t' + name + '\n')
        hf.close()
        print "Done!"
    except IOError, e:
        print e

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
            0x8915, # SIOCGIFADDR
            struct.pack('256s', interface[:15])
        )[20:24])

def is_root():
    """Make sure the script is running as root"""
    if os.geteuid() != 0:
        return False
    return True

def usage():
    print "Usage:\t%s <user> <apikey>" % sys.argv[0]

def check_args(opts, args):
    class ArgumentError(Exception):
        pass

    try:
        if not is_root():
            raise ArgumentError('Y U NO ROOT?')
        elif len(args) is not 2:
            raise ArgumentError('Missing arguments')
        elif len(args[1]) is not 32:
            raise ArgumentError('Invalid API Key')
    except ArgumentError, e:
        sys.stderr.write("[Error] " + str(e) + "\n")
        raise SystemExit(1)
    return (opts, args)

def parse_args():
    u = "%prog [options] <username> <apikey>"
    parser = OptionParser(usage = u,
        description = "Auto-generate /etc/hosts entries for Rackspace Cloud "
            + "Servers" )
    parser.add_option("-p", "--public",
        action = "store_true",
        dest = "public",
        help = "Use Public IP addresses",
        default = False )

    (opts, args) = parser.parse_args()
    return check_args(opts, args)

def main():
    (opts, args) = parse_args()
    cs = cloudservers.Client(args[0], args[1])
    print "Generating new server list for %s..." % args[0]
    servers = cs.get_server_list()
    write_new_hosts(servers, opts)

if __name__ == '__main__':
    main()
