#!/usr/bin/python

"""This is lifted straight from the arsenal client. Really need
   a client library."""

import subprocess
import re
import os
import sys

def facter():
    """Reads in facts from facter"""

    # need this for custom facts - can add additional paths if needed
    os.environ["FACTERLIB"] = "/var/lib/puppet/lib/facter"
    p = subprocess.Popen( ['facter'], stdout=subprocess.PIPE )
    p.wait()
    lines = p.stdout.readlines()
    lines = dict(k.split(' => ') for k in
                   [s.strip() for s in lines if ' => ' in s])

    return lines


def get_uuid():
    """Gets the uuid of a node from dmidecode if available."""

    FNULL = open(os.devnull, 'w')
    p = subprocess.Popen( ['/usr/sbin/dmidecode', '-s', 'system-uuid'], stdout=subprocess.PIPE, stderr=FNULL )
    p.wait()
    uuid = p.stdout.readlines()
    # FIXME: Need some validation here
    if uuid:
        return uuid[0].rstrip()
    else:

        p = subprocess.Popen( ['/usr/sbin/dmidecode', '-t', '1'], stdout=subprocess.PIPE )
        p.wait()
        dmidecode_out = p.stdout.readlines()
        xen_match = "\tUUID: "
        for line in dmidecode_out:
            if re.match(xen_match, line):
                return line[7:].rstrip()

    return None

def get_unique_id(**facts):
    """Determines the unique_id of a node"""

    if facts['kernel'] == 'Linux' or facts['kernel'] == 'FreeBSD':
        if 'ec2_instance_id' in facts:
            unique_id = facts['ec2_instance_id']
        elif os.path.isfile('/usr/sbin/dmidecode'):
            unique_id = get_uuid()
            if not unique_id:
                unique_id = facts['macaddress']
        else:
            unique_id = facts['macaddress']
    else:
        unique_id = facts['macaddress']
    return unique_id


if not os.geteuid() == 0:
    print 'This must run as root.'
    sys.exit(1)


facts = facter()
unique_id = get_unique_id(**facts)

print unique_id

