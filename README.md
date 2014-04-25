# Rackspace Cloud Servers /etc/hosts generator

Auto-populates your /etc/hosts file with the IP addresses (private or public) of First Generation Rackspace Cloud Servers on the account specified by the arguments `username` and `apikey`.

### Installation

For the love of Guido, use virtualenv!
``` bash
$ mkvirtualenv cs-hostgen
New python executable in cs-hostgen/bin/python
Installing setuptools, pip...done.
(cs-hostgen)$ pip install git+git://github.com/DavidWittman/cloudservers-hostsgen.git
```

### Usage

```
usage: cloudservers-hostsgen [-h] [-k] [-p] [-s] username api_key

Auto-generate /etc/hosts entries for Rackspace Cloud Servers

positional arguments:
  username      Rackspace Cloud Username
  api_key       Rackspace Cloud API Key

optional arguments:
  -h, --help    show this help message and exit
  -k, --uk      Use London Auth URL (UK accounts only)
  -p, --public  Use Public IP addresses
  -s, --stdout  Output to stdout
```

### Examples
Add servers to /etc/hosts

``` bash
$ sudo cloudservers-hostsgen example_user 1baabb5ca739bedead7d3beef3c8aa3a
Writing new entries to hosts file... Done!
$ cat /etc/hosts
127.0.0.1  localhost

10.180.1.1	example-01
10.180.1.2	example-02
10.182.1.3	example-03
```

Print server list to stdout

``` bash
$ cloudservers-hostsgen -s example_user 1baabb5ca739bedead7d3beef3c8aa3a
10.180.1.1      example-01
10.180.1.2      example-02
10.182.1.3      example-03
```
