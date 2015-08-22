#!/bin/bash

#
# outputs a sorted list of vm's currently running on the server
#

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

UNIQUE_ID=`./get_unique_id.py`

SERVER_UUID="$(/opt/xensource/bin/list_domains -domid 0 -minimal)"
VM_UUIDS="$(/opt/xensource/bin/list_domains -minimal | grep -v $SERVER_UUID)"
  for VM_UUID in $VM_UUIDS; do
    MAC="$(xe vif-list vm-uuid=$VM_UUID device=0 params=MAC --minimal)"

    # output
    /usr/bin/arsenal -y -l kaboom nodes search unique_id=${MAC} --hypervisor ${UNIQUE_ID}
  done
