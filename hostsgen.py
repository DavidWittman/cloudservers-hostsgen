#!/usr/bin/env python
"""
CloudServers /etc/hosts Generator
Author: David Wittman <david@wittman.com>
	
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

import novaclient.v1_0.client as nova

def parse_hosts(servers, public=False):
    """Generates /etc/hosts format from API output"""

    ip_type = public is True and "public_ip" or "private_ip"
    return ((s.name, getattr(s, ip_type)[0]) for s in servers)

def write_new_hosts(servers):
    """Writes new Cloud Servers to the hosts file.
    
    Args:
        servers: A dictionary of the servers (key) and 
            their IP address (value).

    >>> write_new_hosts({'web01':'10.180.1.42'})
    """

    sys.stdout.write("Writing new entries to /etc/hosts... ")
    try:
        hf = open('/etc/hosts', 'r+')
        hosts = hf.read()
        # Make sure we don't add an entry for this server
        try:
            hosts += get_local_ip('eth1')
        except:
            sys.stderr.write("[Warning] Unable to retrieve local IP address for eth1\n")
	    
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
        if not is_root() and not opts.stdout:
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
    parser.add_option("-k", "--uk",
        action = "store_true",
        dest = "uk",
        help = "Use London Auth URL (UK accounts only)",
        default = False )
    parser.add_option("-p", "--public",
        action = "store_true",
        dest = "public",
        help = "Use Public IP addresses",
        default = False )
    parser.add_option("-s", "--stdout",
        action = "store_true",
        dest = "stdout",
        help = "Output to stdout",
        default = False )

    (opts, args) = parser.parse_args()
    return check_args(opts, args)

def main():
    (opts, args) = parse_args()
    auth_url = opts.uk and "https://lon.auth.api.rackspacecloud.com/v1.0" \
                       or "https://auth.api.rackspacecloud.com/v1.0"
    api = nova.Client(args[0], args[1], None, auth_url)
    servers = parse_hosts(api.servers.list(), opts.public)

    if opts.stdout:
        for (name, ip) in servers:
            print "%s\t%s" % (ip, name)
    else:
        write_new_hosts(servers)

if __name__ == '__main__':
    main()

# vim: set expandtab ts=4 sw=4 sts=4:
