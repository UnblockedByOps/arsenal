#!/bin/bash

usage () {
cat << EOF

usage:$0 options

Runs the Arsenal client and performs tests to ensure the client 
functionality works as expected.

OPTIONS:
       -h      Show this message.
       -p      Python version to test with
       -s      The name of the Arsenal server to connect to. Defaults
               to arsenal.

EOF
}

validate_command () {

  CMD=$1
  expected_ret=$2
  test_mode=$3
  expected_text=
  test_command=
  command_result=
  test_num=$((test_num+1))

  if [ "$test_mode" == "string" ] ; then
      expected_text=$4
  elif [ "$test_mode" == "command" ] ; then
      test_command=$4
      command_result=$5
  fi

  echo -e "\nTEST $test_num START: $CMD\n"
  results=$(eval "$CMD")
  ret_code=$?
  if [[ "$ret_code" == "$expected_ret" ]]; then 
      echo -e "Expected return code received ($expected_ret). Command results:\n"
      echo "$results"
      if [ -n "$expected_text" ] ; then
          if [[ $results =~ "${expected_text}" ]] ; then
              echo -e "\nTEST $test_num RESULT: PASSED\n"
          else
              echo -e "\nTEST $test_num RESULT: FAILED\n"
              FAILED_TESTS+=("TEST $test_num $CMD")
              overall_ret=1
          fi
      elif [ -n "$test_command" ] ; then
          echo -e "\nExecuting test command: $test_command\n"
          cmd_result=$(eval "$test_command")
          echo "Command result: $cmd_result"
          if [[ $cmd_result =~ "${command_result}" ]] ; then
              echo -e "\nTEST $test_num RESULT: PASSED\n"
          else
              echo -e "\nTEST $test_num RESULT: FAILED\n"
              FAILED_TESTS+=("TEST $test_num $CMD")
              overall_ret=1
          fi
      else
          echo -e "\nTEST $test_num RESULT: PASSED\n"
      fi
  else
      echo -e "Expected return code NOT received. Expected: $expected_ret Got: $ret_code Command results:\n"
      echo "$results"
      echo -e "\nTEST $test_num RESULT: FAILED\n"
      FAILED_TESTS+=("TEST $test_num $CMD")
      overall_ret=1
  fi

}

# Parse options
while getopts "hp:s:" OPTION; do
    case $OPTION in
        h)
            usage
            exit 1
            ;;
        p)
            python_version="$OPTARG"
            ;;
        s)
            server="$OPTARG"
            ;;
        ?)
            usage
            exit 1
            ;;
    esac
done

overall_ret=0
test_num=0
FAILED_TESTS=()
arsenal_cmd="python${python_version} bin/arsenal"
ro_conf="/app/arsenal/conf/arsenal-jenkins-regression-readonly.ini"
ro_cookie="/var/lib/jenkins/.arsenal_client_test_cookie_readonly"
rw_conf="/app/arsenal/conf/arsenal-jenkins-regression.ini"
rw_cookie="/var/lib/jenkins/.arsenal_client_test_cookie_readwrite"

if [[ -z "$server" ]] ; then
    server="arsenal"
fi

search_cmd="${arsenal_cmd} --server ${server}"
rw_cmd="${arsenal_cmd} --server ${server} -y -l jenkins-techops -s ${rw_conf} -k ${rw_cookie}"
ro_cmd="${arsenal_cmd} --server ${server} -y -l readonly -s ${ro_conf} -k ${ro_cookie}"

#
# Parameter validation
#
validate_command "${ro_cmd} nodes search name --status=inservice" 0 "string" "400: Bad Request. You must have at least one search parameter."
#
# Add and manipulate objects
#
# Create node
validate_command "${rw_cmd} nodes create --name fopd-TEST8675.internal --unique_id i-123456 --status_id 1" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields all" 0 "string" "name: fopd-TEST8675.internal"
# Delete node by name
validate_command "${rw_cmd} nodes delete --name fopd-TEST8675.internal" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields all" 0 "string" "No results found for search."
# Create node
validate_command "${rw_cmd} nodes create --name fopd-TEST8675.internal --unique_id i-123456 --status_id 1" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields all" 0 "string" "name: fopd-TEST8675.internal"
# Delete node by unique_id
validate_command "${rw_cmd} nodes delete --unique_id i-123456" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields all" 0 "string" "No results found for search."
# Create node
validate_command "${rw_cmd} nodes create --name fopd-TEST8675.internal --unique_id i-123456 --status_id 1" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields all" 0 "string" "name: fopd-TEST8675.internal"
# Delete node by node_id
NODE_ID=$(${arsenal_cmd} -q --server ${server} nodes search name=fopd-TEST8675.internal --exact --fields id | grep ' id:' | awk '{print $2}')
validate_command "${rw_cmd} nodes delete --id ${NODE_ID}" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields all" 0 "string" "No results found for search."
# Create node for testing statuses, node_groups, and tags
validate_command "${rw_cmd} nodes create --name fopd-TEST8675.internal --unique_id i-123456 --status_id 1" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields all" 0 "string" "name: fopd-TEST8675.internal"
# Set status on node to setup
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --status setup" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields status" 0 "string" "name: setup"
# Create node groups
validate_command "${rw_cmd} node_groups create --name TEST_NODE_GROUP1 --owner='nobody@rubiconproject.com' --description 'Rubicon Project TEST'" 0
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP1 --fields all --exact" 0 "string" "name: TEST_NODE_GROUP1"
validate_command "${rw_cmd} node_groups create --name TEST_NODE_GROUP2 --owner='nobody@rubiconproject.com' --description 'Rubicon Project TEST2'" 0
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP2 --fields all --exact" 0 "string" "name: TEST_NODE_GROUP2"
# Assign single node_group to node
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --node_groups TEST_NODE_GROUP1" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields node_groups" 0 "string" "name: TEST_NODE_GROUP1"
# Ensure we see the node_group assigned to the node
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP1 --exact --fields nodes" 0 "string" "name: fopd-TEST8675.internal"
# Deassign single node_group from node
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --del_node_groups TEST_NODE_GROUP1" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields node_groups" 0 "string" "node_groups: []"

# Assign multiple node_groups to node
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --node_groups TEST_NODE_GROUP1" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields node_groups" 0 "string" "name: TEST_NODE_GROUP1"
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --node_groups TEST_NODE_GROUP2" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields node_groups" 0 "string" "name: TEST_NODE_GROUP2"
# Ensure we see the node_groups assigned to the node
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP1 --exact --fields nodes" 0 "string" "name: fopd-TEST8675.internal"
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP2 --exact --fields nodes" 0 "string" "name: fopd-TEST8675.internal"
# Deassign all node_groups from node
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --del_all_node_groups" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields node_groups" 0 "string" "node_groups: []"

# Create and assign tag to node
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --tag NODE_TEST_TAG=TEST" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields tags" 0 "string" "name: NODE_TEST_TAG"
# Search for node by it's tag
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal,tag.name=NODE_TEST_TAG,tag.value=TEST --fields all" 0 "string" "name: fopd-TEST8675.internal"
# Search for node by a bogus tag
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal,tag.name=NODE_TEST_TAG,tag.value=BOGUS --fields all" 0 "string" "No results found for search."
# Deassign tag from node
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --del_tag NODE_TEST_TAG=TEST" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields tags" 0 "string" "tags: []"

# Test deleting a tag when one node has it and the other doesn't
validate_command "${rw_cmd} nodes search name=emx0000.docker --tag NODE_TEST_TAG=TEST" 0
validate_command "${rw_cmd} nodes search name='(emx|bck).*docker' --del_tag NODE_TEST_TAG=TEST" 0
validate_command "${search_cmd} nodes search name=emx0000.docker --exact --fields tags" 0 "string" "tags: []"
#
# Bulk tag removal
#
# Create and assign multiple tags to node
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --tag BULK_NODE_TEST_TAG1=TEST" 0
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --tag BULK_NODE_TEST_TAG2=TEST" 0
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --tag BULK_NODE_TEST_TAG3=TEST" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields tags" 0 "string" "name: BULK_NODE_TEST_TAG"
# Deassign all tags from node
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --del_all_tags" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields tags" 0 "string" "tags: []"

# Create and assign tag to node_group
validate_command "${rw_cmd} node_groups search name=TEST_NODE_GROUP1 --tag NODE_GROUP_TEST_TAG=TEST" 0
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP1 --fields tags" 0 "string" "name: NODE_GROUP_TEST_TAG"
# Deassign tag from node_group
validate_command "${rw_cmd} node_groups search name=TEST_NODE_GROUP1 --del_tag NODE_GROUP_TEST_TAG=TEST" 0
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP1 --fields tags" 0 "string" "tags: []"
# Delete node_group by name
validate_command "${rw_cmd} node_groups delete --name TEST_NODE_GROUP1" 0
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP1" 0 "string" "No results found for search."
# Create tag
validate_command "${rw_cmd} tags create --name TAG_TEST_CREATE --value TEST" 0
validate_command "${search_cmd} tags search name=TAG_TEST_CREATE,value=TEST --fields all --exact" 0 "string" "name: TAG_TEST_CREATE"
# Delete tag
validate_command "${rw_cmd} tags delete --name TAG_TEST_CREATE --value TEST" 0
validate_command "${search_cmd} tags search name=TAG_TEST_CREATE,value=TEST --fields all --exact" 0 "string" "No results found for search."
# Make sure we can change a string to an int and back
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --tag test_string=my_string" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields tags" 0 "string" "value: my_string"
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --tag test_string=100" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields tags" 0 "string" "value: 100"
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --tag test_string=my_string" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields tags" 0 "string" "value: my_string"
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --del_tag test_string=my_string" 0
#
# hardware_profiles
#
validate_command "${rw_cmd} hardware_profiles search name=Unknown --rack-color '#000'" 0
validate_command "${search_cmd} hardware_profiles search name=Unknown --exact --fields rack_color" 0 "string" "rack_color: '#000'"
validate_command "${rw_cmd} hardware_profiles search name=Unknown --rack-u 6" 0
validate_command "${search_cmd} hardware_profiles search name=Unknown --exact --fields rack_u" 0 "string" "rack_u: 6"
#
# ip_addresses
#
validate_command "${rw_cmd} ip_addresses search ip_address=10.100.100.1" 0
#
# Try to make changes as a read only user, be sure it doesn't let us.
#
# Create a node
validate_command "${ro_cmd} nodes create --name fopd-TEST8676.internal --unique_id i-654321 --status_id 1" 1 "string" "WARNING - 403: Forbidden"
validate_command "${search_cmd} nodes search name=fopd-TEST8676.internal --exact --fields all" 0 "string" "No results found for search."
# Delete a node by name
validate_command "${ro_cmd} nodes delete --name fopd-TEST8675.internal" 1 "string" "WARNING - 403: Forbidden"
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields all" 0 "string" "name: fopd-TEST8675.internal"
# Delete a node by unique_id
validate_command "${ro_cmd} nodes delete --unique_id i-123456" 1 "string" "WARNING - 403: Forbidden"
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields all" 0 "string" "name: fopd-TEST8675.internal"
# Delete a node by node_id
NODE_ID=$(${arsenal_cmd} -q --server ${server} nodes search name=fopd-TEST8675.internal --exact --fields id | grep ' id:' | awk '{print $2}')
validate_command "${ro_cmd} nodes delete --id ${NODE_ID} " 1 "string" "WARNING - 403: Forbidden"
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields all" 0 "string" "name: fopd-TEST8675.internal"
# Set status on a node.
validate_command "${ro_cmd} nodes search name=fopd-TEST8675.internal --status hibernating" 1 "string" "WARNING - 403: Forbidden"
# Create a node group
validate_command "${ro_cmd} node_groups create --name TEST_NODE_GROUP_FORBIDDEN --owner='nobody@rubiconproject.com' --description 'Rubicon Project TEST_FORBIDDEN'" 1 "string" "WARNING - 403: Forbidden"
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP_FORBIDDEN --fields all" 0 "string" "No results found for search."
# Assign a node group to a node (first have to create a valid node group)
validate_command "${rw_cmd} node_groups create --name TEST_NODE_GROUP_FORBIDDEN --owner='nobody@rubiconproject.com' --description 'Rubicon Project TEST_FORBIDDEN'" 0
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP_FORBIDDEN --fields all" 0 "string" "name: TEST_NODE_GROUP_FORBIDDEN"
validate_command "${ro_cmd} nodes search name=fopd-TEST8675.internal --node_groups TEST_NODE_GROUP_FORBIDDEN" 1 "string" "WARNING - 403: Forbidden"
# Deassign a node group from a node (first have to do a valid assignemnt)
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --node_groups TEST_NODE_GROUP_FORBIDDEN" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields node_groups" 0 "string" "name: TEST_NODE_GROUP_FORBIDDEN"
validate_command "${search_cmd} -y -l readonly -s ${ro_conf}  -k ${ro_cookie} nodes search name=fopd-TEST8675.internal --del_node_groups TEST_NODE_GROUP_FORBIDDEN" 1 "string" "WARNING - 403: Forbidden"
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields node_groups" 0 "string" "name: TEST_NODE_GROUP_FORBIDDEN"
# Create and assign secure tag to node
validate_command "${ro_cmd} nodes search name=fopd-TEST8675.internal --tag sec_NODE_TEST_TAG_FORBIDDEN=TEST" 1 "string" "WARNING - 403: Forbidden"
validate_command "${ro_cmd} nodes search name=fopd-TEST8675.internal --exact --fields tags" 0 "string" "tags: []"
# Deassign secure tag from node (first have to do a valid assignemnt)
validate_command "${rw_cmd} nodes search name=fopd-TEST8675.internal --tag sec_NODE_TEST_TAG_FORBIDDEN=TEST" 0
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields tags" 0 "string" "name: sec_NODE_TEST_TAG_FORBIDDEN"
validate_command "${ro_cmd} nodes search name=fopd-TEST8675.internal --del_tag sec_NODE_TEST_TAG_FORBIDDEN=TEST" 1 "string" "WARNING - 403: Forbidden"
validate_command "${search_cmd} nodes search name=fopd-TEST8675.internal --exact --fields tags" 0 "string" "name: sec_NODE_TEST_TAG_FORBIDDEN"
# Create and assign secure tag to node_group
validate_command "${ro_cmd} node_groups search name=TEST_NODE_GROUP_FORBIDDEN --tag sec_NODE_GROUP_TEST_TAG_FORBIDDEN=TEST" 1 "string" "WARNING - 403: Forbidden"
validate_command "${ro_cmd} node_groups search name=TEST_NODE_GROUP_FORBIDDEN --fields tags" 0 "string" "tags: []"
# Deassign secure tag from node_group (first have to do a valid assignemnt)
validate_command "${rw_cmd} node_groups search name=TEST_NODE_GROUP_FORBIDDEN --tag sec_NODE_GROUP_TEST_TAG_FORBIDDEN=TEST" 0
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP_FORBIDDEN --fields tags" 0 "string" "name: sec_NODE_GROUP_TEST_TAG_FORBIDDEN"
validate_command "${ro_cmd} node_groups search name=TEST_NODE_GROUP_FORBIDDEN --del_tag sec_NODE_GROUP_TEST_TAG_FORBIDDEN=TEST" 1 "string" "WARNING - 403: Forbidden"
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP_FORBIDDEN --fields tags" 0 "string" "name: sec_NODE_GROUP_TEST_TAG_FORBIDDEN"
# Delete node_group by name
validate_command "${ro_cmd} node_groups delete --name TEST_NODE_GROUP_FORBIDDEN" 1 "string" "WARNING - 403: Forbidden"
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP_FORBIDDEN --fields all" 0 "string" "name: TEST_NODE_GROUP_FORBIDDEN"
#
# network_interfaces
#
validate_command "${rw_cmd} network_interfaces search unique_id=00:11:22:aa:bb:cc" 0
#
# Regex search testing
#
# Create a few more nodes
validate_command "${rw_cmd} nodes create --name fopd-TEST8677.internal --unique_id i-123457 --status_id 1" 0
validate_command "${rw_cmd} nodes create --name fopd-TEST8678.internal --unique_id i-123458 --status_id 1" 0
# Regex nodes search
validate_command "${rw_cmd} nodes search name=fopd-TEST867[78].internal" 0 "command" "echo \"\$results\" | egrep -c 'fopd-TEST867[78].internal'" "2"
# Regex node_groups search
#  Have to re-create this node_group
validate_command "${rw_cmd} node_groups create --name TEST_NODE_GROUP1 --owner='nobody@rubiconproject.com' --description 'Rubicon Project TEST'" 0
#  Assign the node group
validate_command "${rw_cmd} nodes search name=fopd-TEST8677.internal --node_groups TEST_NODE_GROUP1" 0
validate_command "${rw_cmd} nodes search name=fopd-TEST8677.internal --node_groups TEST_NODE_GROUP2" 0
validate_command "${rw_cmd} node_groups search name=TEST_NODE_GROUP[12] --fields nodes" 0 "command" "echo \"\$results\" | grep -c 'fopd-TEST8677.internal'" "2"
#
# Exclude search testing
#
validate_command "${rw_cmd} nodes search name=fopd-TEST867[78].internal --exclude name=fopd-TEST8677.internal" 0 "command" "echo \"\$results\" | egrep -c 'fopd-TEST8678.internal'" "1"
validate_command "${rw_cmd} nodes search name=fopd-TEST867[78].internal --exclude operating_system=Unknown" 0 "command" "echo \"\$results\" | egrep -c 'fopd-TEST'" "0"
#
# datetime search
#
validate_command "${rw_cmd} nodes search name=node000.*datetime,last_registered='<2020-06-16'" 0 "command" "echo \"\$results\" | egrep -c 'node000[01].datetime'" "2"
validate_command "${rw_cmd} nodes search name=node000.*datetime,last_registered='>2020-06-16'" 0 "command" "echo \"\$results\" | egrep -c 'node000[23].datetime'" "2"
validate_command "${rw_cmd} nodes search name=node000.*datetime,last_registered='2020-05-01,2020-09-01'" 0 "command" "echo \"\$results\" | egrep -c 'node000[01].datetime'" "2"
validate_command "${rw_cmd} nodes search name=node000.*datetime,last_registered='2020-05-01,2020-10-01 13:00:00'" 0 "command" "echo \"\$results\" | egrep -c 'node000[012].datetime'" "3"
#
#
# Malformed command testing
#
# Node Create
validate_command "${rw_cmd} nodes create --unique_id i-123456 --status_id 1" 2
validate_command "${rw_cmd} nodes create --name fopd-TEST8675.internal --status_id 1" 2
validate_command "${rw_cmd} nodes create --name fopd-TEST8675.internal --unique_id i-123456" 2
# Node Group Create
validate_command "${rw_cmd} node_groups create --owner='nobody@rubiconproject.com' --description 'Rubicon Project TEST'" 2
validate_command "${rw_cmd} node_groups create --name TEST_NODE_GROUP_INVALID --description 'Rubicon Project TEST'" 2
validate_command "${rw_cmd} node_groups create --name TEST_NODE_GROUP_INVALID --owner='nobody@rubiconproject.com'" 2
# Tag create
validate_command "${rw_cmd} tags create --name FAIL" 2
validate_command "${rw_cmd} tags create --value FAIL" 2
#
#
# Modify object attributes
#
# Modify node group attributes
validate_command "${rw_cmd} node_groups search name=TEST_NODE_GROUP1 --description 'Infra, you LOVE it.'" 0
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP1 --fields all --exact" 0 "string" "description: Infra, you LOVE it."
validate_command "${rw_cmd} node_groups search name=TEST_NODE_GROUP1 --owner 'eng-infra@rubiconproject.com'" 0
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP1 --fields all --exact" 0 "string" "owner: eng-infra@rubiconproject.com"
validate_command "${rw_cmd} node_groups search name=TEST_NODE_GROUP1 --notes-url 'https://wiki.rubiconproject.com'" 0
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP1 --fields all --exact" 0 "string" "notes_url: https://wiki.rubiconproject.com"
validate_command "${rw_cmd} node_groups search name=TEST_NODE_GROUP1 --monitoring-contact 'my_pg_team'" 0
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP1 --fields all --exact" 0 "string" "monitoring_contact: my_pg_team"
validate_command "${rw_cmd} node_groups search name=TEST_NODE_GROUP1 --technical-contact 'my_dev_team'" 0
validate_command "${search_cmd} node_groups search name=TEST_NODE_GROUP1 --fields all --exact" 0 "string" "technical_contact: my_dev_team"
# Modify status attribute
validate_command "${rw_cmd} statuses search name=hibernating --description 'Like a bear, it hibernates.'" 0
validate_command "${search_cmd} statuses search name=hibernating --fields all --exact" 0 "string" "description: Like a bear, it hibernates."
#
# physical_locations
#
validate_command "${rw_cmd} physical_locations create --name TEST_LOCATION_1" 0
validate_command "${rw_cmd} physical_locations create --name TEST_LOCATION_2 -a1 '1234 Anywhere St.' -a2 'Suite 200' -c Smalltown -s CA -t 'Jim Jones' -C USA -P 555-1212 -p 00002 -r 'Some Company'" 0
validate_command "${search_cmd} -b physical_locations search name=TEST_LOCATION_2 --fields all --exact" 0 "string" "status: installed"
validate_command "${rw_cmd} physical_locations search name=TEST_LOCATION_1 --status inservice" 0
validate_command "${search_cmd} -b physical_locations search name=TEST_LOCATION_1 --fields all --exact" 0 "string" "status: inservice"
validate_command "${search_cmd} physical_locations search name=TEST_LOCATION,admin_area=CA" 0
validate_command "${rw_cmd} physical_locations delete --name TEST_LOCATION_2" 0
#
# physical_racks
#
validate_command "${rw_cmd} physical_racks create -l TEST_LOCATION_1 -n R100" 0
validate_command "${rw_cmd} physical_racks create -l TEST_LOCATION_1 -n R101" 0
validate_command "${rw_cmd} physical_racks create -l TEST_LOCATION_1 -n R200" 0
validate_command "${rw_cmd} physical_racks create -l TEST_LOCATION_1 -n R300 -o 10.1.1.0" 1
validate_command "${rw_cmd} physical_racks create -l TEST_LOCATION_1 -n R300 -o 10.1.1.0/25" 0
validate_command "${search_cmd} physical_racks search name=R300,physical_location.name=TEST_LOCATION_1 -f all" 0 "command" "echo \"\$results\" | egrep -c 'oob_subnet: 10.1.1.0/25'" "1"
validate_command "${rw_cmd} physical_racks create -l TEST_LOCATION_1 -n R301 -s 10.1.1.128/25" 0
validate_command "${search_cmd} physical_racks search name=R301,physical_location.name=TEST_LOCATION_1 -f all" 0 "command" "echo \"\$results\" | egrep -c 'server_subnet: 10.1.1.128/25'" "1"
validate_command "${rw_cmd} physical_racks create -l TEST_LOCATION_1 -n R302 -o 10.1.2.0/25 -s 10.1.2.128/25" 0
validate_command "${search_cmd} physical_racks search name=R302,physical_location.name=TEST_LOCATION_1 -f all" 0 "command" "echo \"\$results\" | egrep -c 'oob_subnet: 10.1.2.0/25'" "1"
validate_command "${rw_cmd} physical_racks create -l TEST_LOCATION_1 -n R302 -o 10.1.44.0/25" 0
validate_command "${search_cmd} physical_racks search name=R302,physical_location.name=TEST_LOCATION_1 -f all" 0 "command" "echo \"\$results\" | egrep -c 'oob_subnet: 10.1.44.0/25'" "1"
validate_command "${rw_cmd} physical_racks search name=R302,physical_location.name=TEST_LOCATION_1 -o 10.1.45.0/25" 0
validate_command "${search_cmd} physical_racks search name=R302,physical_location.name=TEST_LOCATION_1 -f all" 0 "command" "echo \"\$results\" | egrep -c 'oob_subnet: 10.1.45.0/25'" "1"
validate_command "${search_cmd} physical_racks search name=R302,physical_location.name=TEST_LOCATION_1 -f all" 0 "command" "echo \"\$results\" | egrep -c 'server_subnet: 10.1.2.128/25'" "1"
validate_command "${search_cmd} physical_racks search name=R10,physical_location.name=TEST_LOCATION_1 -f all" 0 "command" "echo \"\$results\" | egrep -c 'name: TEST_LOCATION_1'" "2"
validate_command "${rw_cmd} physical_racks create -l TEST_LOCATION_3 -n R100" 1
#
# physical_elevations
#
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R100 -e 1" 0
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R100 -e 2" 0
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R100 -e 3" 0
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R100 -e 4" 0
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R100 -e 5" 0
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R100 -e 6" 0
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R100 -e 7" 0
validate_command "${search_cmd} physical_racks search physical_location.name=TEST_LOCATION_1,name=R100 -f all" 0 "string" "name: TEST_LOCATION_1"
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R200 -e 1" 0
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R200 -e 2" 0
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R200 -e 3" 0
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R200 -e 4" 0
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R200 -e 5" 0
validate_command "${search_cmd} physical_racks search physical_location.name=TEST_LOCATION_1,name=R200 -f all" 0 "string" "name: TEST_LOCATION_1"
#
# physical_devices
#
validate_command "${rw_cmd} physical_devices create -s aabb1234500 -H 'HP ProLiant DL360 Gen9' -l TEST_LOCATION_1 -r R100 -e 1 -i 10.99.1.1 -m 00:aa:11:bb:22:cc -m1 44:55:66:aa:bb:c0 -m2 44:55:66:aa:bb:c1 -R 2024-08-01" 0
validate_command "${search_cmd} physical_devices search serial_number=AABB1234500 --fields all --exact" 0 "string" "mac_address_1: 44:55:66:aa:bb:c0"
validate_command "${rw_cmd} physical_devices create -s aabb1234501 -H 'HP ProLiant DL360 Gen9' -l TEST_LOCATION_1 -r R100 -e 1 -i 10.99.1.2 -m 01:aa:11:bb:22:cc -m1 44:55:66:aa:bb:e0 -m2 44:55:66:aa:bb:e1 -R 2024-08-01" 1 "string" "Physical elevation is already occupied, move the existing physical_device first."
# Make sure things are converted to the proper case
validate_command "${rw_cmd} physical_devices create -s aabb1234502 -H 'HP ProLiant DL360 Gen9' -l TEST_LOCATION_1 -r R100 -e 7 -i 10.99.1.7 -m 07:AA:11:BB:22:CC -m1 77:55:66:AA:BB:C0 -m2 77:55:66:AA:BB:C1 -R 2024-08-01" 0
validate_command "${search_cmd} physical_devices search serial_number=AABB1234502 --fields all --exact" 0 "string" "oob_mac_address: 07:aa:11:bb:22:cc"
validate_command "${search_cmd} physical_devices search serial_number=AABB1234502 --fields all --exact" 0 "string" "mac_address_1: 77:55:66:aa:bb:c0"
validate_command "${search_cmd} physical_devices search serial_number=AABB1234502 --fields all --exact" 0 "string" "mac_address_2: 77:55:66:aa:bb:c1"
# physical_device defaults to available
validate_command "${search_cmd} physical_devices search serial_number=Y00001 --fields all --exact" 0 "string" "name: available"
# set physical_device to  allocated and ensure the status changes.
validate_command "${rw_cmd} physical_devices search serial_number=Y00001 --status allocated" 0
validate_command "${search_cmd} physical_devices search serial_number=Y00001 --fields all --exact" 0 "string" "name: allocated"
# Set the node to decom, ensure the physical_device becomes available
validate_command "${rw_cmd} nodes search name=kvm0000.docker --status decom" 0
validate_command "${search_cmd} physical_devices search serial_number=Y00001 --fields all --exact" 0 "string" "name: available"
# Set the node to hibernating, which is not in the map, ensure the physical_device status remains unchanged
validate_command "${rw_cmd} nodes search name=kvm0000.docker --status hibernating" 0
validate_command "${search_cmd} physical_devices search serial_number=Y00001 --fields all --exact" 0 "string" "name: available"
#
# Boostrapping status changes
#
# Make sure a node going to bootstrapping sets the physical_device status to
# bootstrapping and that the node going to bootstrapped sets the physical_device
# as available.
#
validate_command "${rw_cmd} nodes search name=pd0000.test --status bootstrapping" 0
validate_command "${search_cmd} nodes search name=pd0000.test --exact --fields status" 0 "string" "name: bootstrapping"
validate_command "${search_cmd} physical_devices search serial_number=Y00002 -f status" 0 "string" "name: bootstrapping"
validate_command "${rw_cmd} nodes search name=pd0000.test --status bootstrapped" 0
validate_command "${search_cmd} nodes search name=pd0000.test --exact --fields status" 0 "string" "name: bootstrapped"
validate_command "${search_cmd} physical_devices search serial_number=Y00002 -f status" 0 "string" "name: available"
#
# Make sure a physical_device that already has inservice_date set doesn't
# change when the status goes from bootstrapping -> botstrapped a second time.
#
validate_command "${rw_cmd} physical_devices search serial_number=Y00003 --status bootstrapping" 0
validate_command "${rw_cmd} physical_devices search serial_number=Y00003 --status bootstrapped" 0
validate_command "${search_cmd} physical_devices search serial_number=Y00003 -f inservice_date" 0 "string" "inservice_date: 2024-08-01"
#
# physical_devices updates
# elevation
validate_command "${rw_cmd} physical_devices search serial_number=AABB1234500 -l TEST_LOCATION_1 -r R100 -e 5" 0
validate_command "${search_cmd} physical_devices search serial_number=AABB1234500 -f all" 0 "string" "elevation: '5'"
# rack
validate_command "${rw_cmd} physical_devices search serial_number=AABB1234500 -l TEST_LOCATION_1 -r R100 -e 6" 0
validate_command "${search_cmd} physical_devices search serial_number=AABB1234500 -f all" 0 "string" "name: R100"
validate_command "${search_cmd} physical_devices search serial_number=AABB1234500 -f all" 0 "string" "elevation: '6'"
# oob-ip-address
validate_command "${rw_cmd} physical_devices search serial_number=AABB1234500 --oob-ip-address 1.2.3.4" 0
validate_command "${search_cmd} physical_devices search serial_number=AABB1234500 -f all" 0 "string" "oob_ip_address: 1.2.3.4"
# oob-mac-address
validate_command "${rw_cmd} physical_devices search serial_number=AABB1234500 --oob-mac-address qq:11:zz:22:xx:33" 0
validate_command "${search_cmd} physical_devices search serial_number=AABB1234500 -f all" 0 "string" "oob_mac_address: qq:11:zz:22:xx:33"
# hardware-profile
validate_command "${rw_cmd} physical_devices search serial_number=AABB1234500 -H 'HP ProLiant m710x Server Cartridge'" 0
validate_command "${search_cmd} physical_devices search serial_number=AABB1234500 -f all" 0 "string" "name: HP ProLiant m710x Server Cartridge"
# mac-address-1
validate_command "${rw_cmd} physical_devices search serial_number=AABB1234500 -m1 cq:11:zz:22:xx:33" 0
validate_command "${search_cmd} physical_devices search serial_number=AABB1234500 -f all" 0 "string" "mac_address_1: cq:11:zz:22:xx:33"
# mac-address-2
validate_command "${rw_cmd} physical_devices search serial_number=AABB1234500 -m2 dq:11:zz:22:xx:33" 0
validate_command "${search_cmd} physical_devices search serial_number=AABB1234500 -f all" 0 "string" "mac_address_2: dq:11:zz:22:xx:33"
# received-date
validate_command "${rw_cmd} physical_devices search serial_number=Y00003 --received-date 2024-08-02" 0
# localization casues the date to render as yesterday since dates are inserted as midnight UTC.
validate_command "${search_cmd} physical_devices search serial_number=Y00003 -f all" 0 "string" "received_date: 2024-08-01"
# inservice-date
validate_command "${rw_cmd} physical_devices search serial_number=Y00003 --inservice-date 2024-08-02" 0
# localization casues the date to render as yesterday since dates are inserted as midnight UTC.
validate_command "${search_cmd} physical_devices search serial_number=Y00003 -f all" 0 "string" "inservice_date: 2024-08-01"
#
# Import tool
#
validate_command "${rw_cmd} physical_devices import -c conf/test_physical_device_import.csv" 0
validate_command "${search_cmd} physical_devices search serial_number=A0 -f all" 0 "command" "echo \"\$results\" | egrep -c 'name: TEST_LOCATION_1'" "3"
# Make sure physical_device without a status specified is set to racked
validate_command "${search_cmd} physical_devices search serial_number=A00000002 -f status" 0 "string" "name: racked"
# Make sure physical_device with a status specified has the correct status set
validate_command "${search_cmd} physical_devices search serial_number=A00000003 -f status" 0 "string" "name: allocated"
validate_command "${rw_cmd} physical_devices import -c conf/test_physical_device_import_mixed.csv" 1
validate_command "${rw_cmd} physical_devices import -c conf/test_physical_device_import_no_hw_profile.csv" 1
validate_command "${search_cmd} physical_devices search serial_number=B0 -f all" 0 "command" "echo \"\$results\" | egrep -c 'name: TEST_LOCATION_1'" "3"
validate_command "${rw_cmd} physical_devices import -c conf/test_physical_device_import_fail.csv" 1
# tags
validate_command "${search_cmd} physical_devices search serial_number=A0 -f all" 0 "command" "echo \"\$results\" | egrep -c 'name: chassis_'" "2"
#
# Export tool
#
validate_command "${search_cmd} physical_devices export physical_location.name=TEST_LOCATION_1,serial_number=B0" 0 "command" "echo \"\$results\" | egrep -c 'TEST_LOCATION_1'" "3"
# missing required parameter physical_location.name
validate_command "${search_cmd} physical_devices export serial_number=B0" 1
# tags
validate_command "${search_cmd} physical_devices export physical_location.name=TEST_LOCATION_1,serial_number=A0" 0 "command" "echo \"\$results\" | egrep -c 'chassis_'" "1"
#
# data_centers
#
validate_command "${rw_cmd} data_centers create -n TEST_DATA_CENTER_1 -s setup" "0"
validate_command "${rw_cmd} data_centers create -n TEST_DATA_CENTER_2 -s inservice" "0"
validate_command "${search_cmd} data_centers search name=TEST_DATA_CENTER_1 --fields all" 0 "string" "name: setup"
validate_command "${search_cmd} data_centers search name=TEST_DATA_CENTER_2 --fields all" 0 "string" "name: inservice"
validate_command "${search_cmd} data_centers search name=TEST_DATA_CENTER_ --fields all" 0 "command" "echo \"\$results\" | egrep -c 'name: TEST_DATA_CENTER_'" "2"
validate_command "${rw_cmd} data_centers search name=TEST_DATA_CENTER_1 --status inservice" 0
validate_command "${search_cmd} data_centers search name=TEST_DATA_CENTER_1 --fields all" 0 "string" "name: inservice"
validate_command "${rw_cmd} data_centers delete --name TEST_DATA_CENTER_1" 0
validate_command "${search_cmd} data_centers search name=TEST_DATA_CENTER_ --fields all" 0 "command" "echo \"\$results\" | egrep -c 'name: TEST_DATA_CENTER_'" "1"
#
# ENC
#
# create the node
validate_command "${rw_cmd} nodes create --name fxxp-tst9999.internal --unique_id fxxp-tst9999.internal --status_id 1" 0
# no node group
validate_command "${search_cmd} nodes enc --name fxxp-tst9999.internal" 0 "string" "classes: null"
# create the node_group
validate_command "${rw_cmd} node_groups create --name fxx_tst --owner='nobody' --description 'ENC test node group'" 0
# Still should not have the node_group assigned since it is not in setup or inservice.
validate_command "${search_cmd} nodes enc --name fxxp-tst9999.internal" 0 "string" "classes: null"
# Set the status to an assignable status
validate_command "${rw_cmd} nodes search name=fxxp-tst9999.internal,status=initializing --status setup" 0
# Now it should get the node group
validate_command "${rw_cmd} nodes enc --name fxxp-tst9999.internal" 0 "string" "- fxx_tst"
#
# API change limit tests
#
validate_command "${rw_cmd} nodes search name=docker --del_all_tags" 1 "string" "WARNING - 400: Bad Request. You are trying to change more items in one query than allowed"
validate_command "${rw_cmd} nodes search name=docker --del_all_node_groups" 1 "string" "WARNING - 400: Bad Request. You are trying to change more items in one query than allowed"
validate_command "${rw_cmd} nodes search name=docker --status=decom" 1 "string" "WARNING - 400: Bad Request. You are trying to change more items in one query than allowed"
validate_command "${rw_cmd} nodes search name=docker --node_groups=default_install" 1 "string" "WARNING - 400: Bad Request. You are trying to change more items in one query than allowed"
#
# Clean up
#
validate_command "${rw_cmd} nodes delete --name fopd-TEST8675.internal" 0
validate_command "${rw_cmd} nodes delete --name fopd-TEST8676.internal" 0
validate_command "${rw_cmd} nodes delete --name fopd-TEST8677.internal" 0
validate_command "${rw_cmd} nodes delete --name fopd-TEST8678.internal" 0
validate_command "${rw_cmd} node_groups delete --name TEST_NODE_GROUP1" 0
validate_command "${rw_cmd} node_groups delete --name TEST_NODE_GROUP2" 0
validate_command "${rw_cmd} node_groups delete --name TEST_NODE_GROUP_FORBIDDEN" 0
validate_command "${rw_cmd} tags delete --name NODE_TEST_TAG --value TEST" 0
validate_command "${rw_cmd} tags delete --name NODE_TEST_TAG_FORBIDDEN --value TEST" 0
validate_command "${rw_cmd} tags delete --name sec_NODE_TEST_TAG_FORBIDDEN --value TEST" 0
validate_command "${rw_cmd} tags delete --name NODE_GROUP_TEST_TAG --value TEST" 0
validate_command "${rw_cmd} tags delete --name NODE_GROUP_TEST_TAG_FORBIDDEN --value TEST" 0
validate_command "${rw_cmd} tags delete --name sec_NODE_GROUP_TEST_TAG_FORBIDDEN --value TEST" 0
validate_command "${rw_cmd} tags delete --name TAG_TEST_CREATE --value TEST" 0
validate_command "${rw_cmd} tags delete --name TAG_TEST_CREATE_FORBIDDEN --value TEST" 0
validate_command "${rw_cmd} statuses search name=hibernating --description 'Instances that have been spun down that will be spun up on demand.'" 0
validate_command "${rw_cmd} data_centers delete --name TEST_DATA_CENTER_2" 0


# print out failed tests
if [ -n "$FAILED_TESTS" ] ; then
    echo -e "\nSUMMARY\nThe following tests have failed (${#FAILED_TESTS[@]}):"
    echo -e "----------------------------------------------------------------------\n"
    for i in "${FAILED_TESTS[@]}" ; do
        echo "$i"
    done
    echo -e "\n----------------------------------------------------------------------\n"
fi

exit $overall_ret
