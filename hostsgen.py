#!/usr/bin/env python
"""
CloudServers /etc/hosts Generator
Author: David Wittman <david@wittman.com>

Auto-populates the system's hosts file with IP addresses of Rackspace
Cloud Servers on the account specified by the arguments <user> and
<apikey>. Uses the python-novaclient bindings for API interaction.

"""

import fcntl
import os
import socket
import struct
import sys
from argparse import ArgumentParser

import novaclient.v1_0.client as nova

def parse_hosts(servers, public=False):
    """Generates /etc/hosts format from API output

    :param servers: Cloud Server objects returned from novaclient.
    :type servers: A list of Cloud Server objects.
    :param public: Use public IP address (default=False).
    :type public: bool.
    :returns: A generator containing tuples of hostname and IP
              address mappings.

    """

    ip_type = public is True and "public_ip" or "private_ip"
    return ((s.name, getattr(s, ip_type)[0]) for s in servers)

def write_new_hosts(servers):
    """Writes new Cloud Servers to /etc/hosts

    :param servers: The list of server names and IP addresses.
    :type servers: A list of tuples.

    >>> write_new_hosts([('web01','10.180.1.42')])

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

        :param interface: The local interface to get the IP for
        :type interface: str.
        :returns: str -- The IP address of the interface.

        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915, # SIOCGIFADDR
            struct.pack('256s', interface[:15])
        )[20:24])

def is_root():
    """Make sure the script is running as root

    :returns: bool.

    """
    if os.geteuid() != 0:
        return False
    return True

def usage():
    print "Usage:\t%s <user> <apikey>" % sys.argv[0]

def check_args(args):
    class ArgumentError(Exception):
        pass

    if not is_root() and not args.stdout:
        raise ArgumentError('This script must be run as root, or with the -s '\
                            'flag to output to stdout')
    elif len(args.api_key) is not 32:
        raise ArgumentError('Invalid API Key')

    return args

def parse_args():
    description = "Auto-generate /etc/hosts entries for Rackspace Cloud Servers"
    parser = ArgumentParser(description=description)
    parser.add_argument("-k", "--uk",
        action = "store_true",
        dest = "uk",
        help = "Use London Auth URL (UK accounts only)",
        default = False )
    parser.add_argument("-p", "--public",
        action = "store_true",
        dest = "public",
        help = "Use Public IP addresses",
        default = False )
    parser.add_argument("-s", "--stdout",
        action = "store_true",
        dest = "stdout",
        help = "Output to stdout",
        default = False )
    parser.add_argument("username", help="Rackspace Cloud Username")
    parser.add_argument("api_key", help="Rackspace Cloud API Key")

    return check_args(parser.parse_args())

def main():
    args = parse_args()
    auth_url = args.uk and "https://lon.auth.api.rackspacecloud.com/v1.0" \
                       or "https://auth.api.rackspacecloud.com/v1.0"
    api = nova.Client(args.username, args.api_key, None, auth_url)
    servers = parse_hosts(api.servers.list(), args.public)

    if args.stdout:
        for (name, ip) in servers:
            print "%s\t%s" % (ip, name)
    else:
        write_new_hosts(servers)

if __name__ == '__main__':
    main()

# vim: set expandtab ts=4 sw=4 sts=4:
