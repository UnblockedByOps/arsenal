#!/bin/bash
#  Copyright 2015 CityGrid Media, LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#
# outputs a sorted list of vm's currently running on the xen server
#
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo "INFO    - Determining unique_id of hypervisor"
UNIQUE_ID=`/app/arsenal/bin/get_unique_id.py`

echo "INFO    - Retrieivng list of vms on this hypervisor"
SERVER_UUID="$(/opt/xensource/bin/list_domains -domid 0 -minimal)"
VM_UUIDS="$(/opt/xensource/bin/list_domains -minimal | grep -v $SERVER_UUID)"

echo "INFO    - Reporting to arsenal"
for VM_UUID in $VM_UUIDS; do
  MAC="$(xe vif-list vm-uuid=$VM_UUID device=0 params=MAC --minimal)"

  # output
  CMD="/usr/bin/arsenal -y -l hvm nodes search unique_id=${MAC} --hypervisor ${UNIQUE_ID}"
  echo "INFO    - Executing: ${CMD}"
  ${CMD}
done
