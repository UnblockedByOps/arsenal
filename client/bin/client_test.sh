#!/bin/bash

usage () {
cat << EOF

usage:$0 options

Runs the Arsenal client and performs tests to ensure the client 
functionality works as expected.

OPTIONS:
       -h      Show this message.
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

overall_ret=0
test_num=0
FAILED_TESTS=()
arsenal_cmd="python2.7 bin/arsenal"
ro_conf="/app/arsenal/conf/arsenal-jenkins-regression-readonly.ini"
ro_cookie="/var/lib/jenkins/.arsenal_cookie_readonly"
rw_conf="/app/arsenal/conf/arsenal-jenkins-regression.ini"

# Parse options
while getopts "hs:" OPTION; do
    case $OPTION in
        h)
            usage
            exit 1
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

if [[ -z "$server" ]] ; then
    server="arsenal"
fi

search_cmd="${arsenal_cmd} --server ${server}"
rw_cmd="${arsenal_cmd} --server ${server} -y -l jenkins-techops -s ${rw_conf}"
ro_cmd="${arsenal_cmd} --server ${server} -y -l readonly -s ${ro_conf} -k ${ro_cookie}"

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
# Modify status attribute
validate_command "${rw_cmd} statuses search name=hibernating --description 'Like a bear, it hibernates.'" 0
validate_command "${search_cmd} statuses search name=hibernating --fields all --exact" 0 "string" "description: Like a bear, it hibernates."
#
# physical_locations
#
validate_command "${rw_cmd} physical_locations create --name TEST_LOCATION_1" 0
validate_command "${rw_cmd} physical_locations create --name TEST_LOCATION_2 -a1 '1234 Anywhere St.' -a2 'Suite 200' -c Smalltown -s CA -t 'Jim Jones' -C USA -P 555-1212 -p 00002 -r 'Some Company'" 0
validate_command "${search_cmd} physical_locations search name=TEST_LOCATION,admin_area=CA" 0
validate_command "${rw_cmd} physical_locations delete --name TEST_LOCATION_2" 0
#
# physical_racks
#
validate_command "${rw_cmd} physical_racks create -l TEST_LOCATION_1 -n R100" 0
validate_command "${rw_cmd} physical_racks create -l TEST_LOCATION_1 -n R101" 0
validate_command "${search_cmd} physical_racks search name=R10,physical_location.name=TEST_LOCATION_1" 0
validate_command "${rw_cmd} physical_racks create -l TEST_LOCATION_3 -n R100" 1
#
# physical_elevations
#
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R100 -e 1" 0
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R100 -e 2" 0
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R100 -e 3" 0
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R100 -e 4" 0
validate_command "${rw_cmd} physical_elevations create -l TEST_LOCATION_1 -r R100 -e 5" 0
validate_command "${search_cmd} physical_racks search physical_location.name=TEST_LOCATION_1,name=R100 -f all" 0
#
# physical_devices
#

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
