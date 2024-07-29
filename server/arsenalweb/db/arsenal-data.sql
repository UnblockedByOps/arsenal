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
use arsenal;

# Initial Admin password is 'password'
INSERT INTO users VALUES (1, 'admin', 'Admin', 'Superuser', 'Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', NOW(), NOW(), 'Admin');
# Initial kaboom password is 'password'
INSERT INTO users VALUES (2, 'kaboom', 'Register', 'Bot', 'Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', NOW(), NOW(), 'Admin');
# Initial hvm password is 'test'
INSERT INTO users VALUES (3, 'hvm', 'Hypervisor Vm', 'Bot', 'MRM/VA0wb3zbpkOq', '$6$rounds=656000$MRM/VA0wb3zbpkOq$i5GhDFjIFj9IgRmhEgxWvmt0U6VOUQp5K6XGCn/ExuieuJu8xA7Oxqc6.SVUaM0wjXgyQBw188L3ZVxolC6/m1', NOW(), NOW(), 'Admin');
# Initial readonly password is 'readonly'
INSERT INTO users VALUES (4, 'readonly', 'Readonly', 'User', 'AT4beMbzo1zYZRFN', '$6$rounds=656000$AT4beMbzo1zYZRFN$VbEbyjQUY7xdlHALvD.0DoN9ZhyGNR89iMRI.03BwlW9bi1b3msegIThlmo0M1yZpy3jNagdXpjZhk3/sXWSB0', NOW(), NOW(), 'Admin');
# Initial jenkins-techops password is 'password'
INSERT INTO users VALUES (5, 'jenkins-techops', 'jenkins-techops', 'Bot', 'Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', NOW(), NOW(), 'Admin');
# Initial puppet-enc password is 'password'
INSERT INTO users VALUES (6, 'puppet-enc', 'Puppet Node Classifier', 'Bot', 'Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', NOW(), NOW(), 'Admin');
# Initial aws-lambda password is 'password'
INSERT INTO users VALUES (7, 'aws-lambda', 'AWS Lambda user for ec2 decom', 'Bot', 'Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', NOW(), NOW(), 'Admin');
# Initial release password is 'password'
INSERT INTO users VALUES (8, 'release', 'Bot user for automated releases', 'Bot', 'Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', NOW(), NOW(), 'Admin');
# Initial external-enc password is 'password'
INSERT INTO users VALUES (9, 'external-enc', 'External (non-puppet) Node Classifier', 'Bot', 'Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', NOW(), NOW(), 'Admin');
# Initial decom-hw password is 'password'
INSERT INTO users VALUES (10, 'decom-hw', 'Bot user to decommission harware', 'Bot', 'Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', NOW(), NOW(), 'Admin');

#
# GROUPS
#
# database groups
###########################################################################
INSERT INTO groups VALUES (1,   'local_admin',               NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (2,   'api_write',                 NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (3,   'api_register',              NOW(), NOW(), 'Admin');
# Set this to whatever system group you want to have admin access (wheel, arsenal_admins, etc.)
INSERT INTO groups VALUES (4,   'arsenal_admins',NOW(),NOW(), 'Admin');
# For devel on mac
# INSERT INTO groups VALUES (5,  'admin',                     NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (6,   'node_write',                NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (7,   'node_delete',               NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (8,   'node_group_write',          NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (9,   'node_group_delete',         NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (10,  'tag_write',                 NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (11,  'tag_delete',                NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (12,  'data_center_write',         NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (13,  'data_center_delete',        NOW(), NOW(), 'Admin');
# This is a special local group that is not assigned any permissions via route, but 
# members of this group will be able to write secure tags.
INSERT INTO groups VALUES (14,  'secure_tags',               NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (15,  'physical_device_write',     NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (16,  'physical_device_delete',    NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (17,  'physical_location_write',   NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (18,  'physical_location_delete',  NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (19,  'physical_rack_write',       NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (20,  'physical_rack_delete',      NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (21,  'physical_elevation_write',  NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (22,  'physical_elevation_delete', NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (23,  'status_write',              NOW(), NOW(), 'Admin');
# Site specific groups should be above id 100
INSERT INTO groups VALUES (100, 'rp_noc',                    NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (101, 'override_ratio',            NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (102, 'dcops',                     NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (103, 'devs',                      NOW(), NOW(), 'Admin');

# Group permissions that can be assigned to groups
###########################################################################
INSERT INTO group_perms VALUES (1,  'admin',                     NOW());
INSERT INTO group_perms VALUES (2,  'api_write',                 NOW());
INSERT INTO group_perms VALUES (3,  'api_register',              NOW());
INSERT INTO group_perms VALUES (4,  'node_write',                NOW());
INSERT INTO group_perms VALUES (5,  'node_delete',               NOW());
INSERT INTO group_perms VALUES (6,  'node_group_write',          NOW());
INSERT INTO group_perms VALUES (7,  'node_group_delete',         NOW());
INSERT INTO group_perms VALUES (8,  'tag_write',                 NOW());
INSERT INTO group_perms VALUES (9,  'tag_delete',                NOW());
INSERT INTO group_perms VALUES (10, 'data_center_write',         NOW());
INSERT INTO group_perms VALUES (11, 'data_center_delete',        NOW());
INSERT INTO group_perms VALUES (12, 'physical_device_write',     NOW());
INSERT INTO group_perms VALUES (13, 'physical_device_delete',    NOW());
INSERT INTO group_perms VALUES (14, 'physical_location_write',   NOW());
INSERT INTO group_perms VALUES (15, 'physical_location_delete',  NOW());
INSERT INTO group_perms VALUES (16, 'physical_rack_write',       NOW());
INSERT INTO group_perms VALUES (17, 'physical_rack_delete',      NOW());
INSERT INTO group_perms VALUES (18, 'physical_elevation_write',  NOW());
INSERT INTO group_perms VALUES (19, 'physical_elevation_delete', NOW());
INSERT INTO group_perms VALUES (20, 'status_write',              NOW());

# Assigning group permissions to groups
###########################################################################
#  local_admin gets all perms
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,1);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,2);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,3);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,4);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,5);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,6);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,7);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,8);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,9);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,10);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,11);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,12);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,13);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,14);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,15);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,16);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,17);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,18);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,19);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (1,20);
#  api_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (2,2);
#  api_register
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (3,3);
#  arsenal_admins (system admin) gets all perms
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,1);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,2);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,3);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,4);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,5);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,6);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,7);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,8);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,9);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,10);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,11);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,12);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,13);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,14);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,15);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,16);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,17);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,18);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,19);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (4,20);
#  node_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (6,4);
#  node_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (7,5);
#  node_group_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (8,6);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (100,6);
#  node_group_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (9,7);
#  tag_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (10,8);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (101,8);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (103,8);
#  tag_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (11,9);
#  data_center_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (12,10);
#  data_center_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (13,11);
#  physical_device_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (15,12);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (102,12);
#  physical_device_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (16,13);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (102,13);
#  physical_location_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (17,14);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (102,14);
#  physical_location_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (18,15);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (102,15);
#  physical_rack_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (19,16);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (102,16);
#  physical_rack_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (20,17);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (102,17);
#  physical_elevation_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (21,18);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (102,18);
#  physical_elevation_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (22,19);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (102,19);
#  status_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (23,20);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (100,20);
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (102,20);

# For devel on mac
# INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (5,1);
# INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (5,2);
# INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (5,3);

# Adding db users to db groups.
###########################################################################
### Becasue we need to allow kaboom to update status, any user added 
### to the api_write group also needs to be added to the api_register group.
# admin           = 1
# kaboom          = 2
# hvm             = 3
# readonly        = 4
# jenkins-techops = 5
# puppet-enc      = 6
# aws-lambda      = 7
# release         = 8
# external-enc    = 9
# decom-hw        = 10
# Add user: local_admin to groups: local_admin
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (1, 1);
# Add user: hvm to groups: api_register, status_write
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (2, 3);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (23, 3);
# Add user: jenkins-techops to groups: api_write, api_register, node_write, node_group_delete, tag_write, tag_delete, secure_tags, status_write
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (2, 5);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (3, 5);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (6, 5);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (7, 5);
# INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (8, 5); # node_group_write - inf1 only
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (9, 5);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (10, 5);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (14, 5);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (11, 5);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (23, 5);
# Add user: kaboom to groups: api_register, node_write, status_write
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (3, 2);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (6, 2);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (23, 2);
# Add user: puppet-enc to groups: node_write, node_group_write, secure_tags
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (6, 6);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (8, 6);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (14, 6);
# Add user: aws-lambda to groups: api_register, status_write
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (3, 7);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (23, 7);
# Add user: release to groups: tag_write, tag_delete, secure_tags
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (10, 8);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (11, 8);
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (14, 8);
# Add user: external-enc to groups: node_group_write
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (8, 9);
# Add user: decom-hw to groups: physical_device_delete
INSERT INTO local_user_group_assignments (group_id,user_id) VALUES (16, 10);

#
# STATUSES
#
INSERT INTO statuses VALUES (1, 'initializing', 'Instances in the process of spinning up.', NOW(), NOW(), 'Admin');
INSERT INTO statuses_audit VALUES (1, 1, 'name', 'created', 'initializing', NOW(), 'Admin');
INSERT INTO statuses VALUES (2, 'installed', 'New node with OS installed and base configuration applied.', NOW(), NOW(), 'Admin');
INSERT INTO statuses_audit VALUES (2, 2, 'name', 'created', 'installed', NOW(), 'Admin');
INSERT INTO statuses VALUES (3, 'setup', 'New node fully configured and awaiting production deployment.', NOW(), NOW(), 'Admin');
INSERT INTO statuses_audit VALUES (3, 3, 'name', 'created', 'setup', NOW(), 'Admin');
INSERT INTO statuses VALUES (4, 'inservice', 'Hardware and OS functional, applications running.', NOW(), NOW(), 'Admin');
INSERT INTO statuses_audit VALUES (4, 4, 'name', 'created', 'inservice', NOW(), 'Admin');
INSERT INTO statuses VALUES (5, 'hibernating', 'Instances that have been spun down that will be spun up on demand.', NOW(), NOW(), 'Admin');
INSERT INTO statuses_audit VALUES (5, 5, 'name', 'created', 'hibernating', NOW(), 'Admin');
INSERT INTO statuses VALUES (6, 'decom', 'Nodes that are dead and gone.', NOW(), NOW(), 'Admin');
INSERT INTO statuses_audit VALUES (6, 6, 'name', 'created', 'decom', NOW(), 'Admin');
INSERT INTO statuses VALUES (7, 'available', 'Hardware that is available to be re-purposed.', NOW(), NOW(), 'Admin');
INSERT INTO statuses_audit VALUES (7, 7, 'name', 'created', 'available', NOW(), 'Admin');
INSERT INTO statuses VALUES (8, 'broken', 'Hardware that is in need of repair.', NOW(), NOW(), 'Admin');
INSERT INTO statuses_audit VALUES (8, 8, 'name', 'created', 'broken', NOW(), 'Admin');
INSERT INTO statuses VALUES (9, 'maintenance', 'Hardware that is currently undergoing maintenance.', NOW(), NOW(), 'Admin');
INSERT INTO statuses_audit VALUES (9, 9, 'name', 'created', 'maintenance', NOW(), 'Admin');
INSERT INTO statuses VALUES (10, 'allocated', 'Hardware that has been allocated for a purpose.', NOW(), NOW(), 'Admin');
INSERT INTO statuses_audit VALUES (10, 10, 'name', 'created', 'allocated', NOW(), 'Admin');
INSERT INTO statuses VALUES (11, 'pending_maintenance', 'Node that is marked for maintenance..', NOW(), NOW(), 'Admin');
INSERT INTO statuses_audit VALUES (11, 11, 'name', 'created', 'allocated', NOW(), 'Admin');

INSERT INTO node_groups VALUES (1, 'default_install', 'admin@rubiconproject.com', 'Default node group for all nodes.', 'http://my/documentation', 'pagerduty_24x7',NOW(), NOW(), 'Admin');
INSERT INTO node_groups_audit VALUES (1, 1, 'name', 'created', 'default_install', NOW(), 'Admin');

INSERT INTO hardware_profiles VALUES (1, 'Unknown', 'Unknown', 'Unknown', 1, '#fff', NOW(), NOW(), 'Admin');
INSERT INTO hardware_profiles_audit VALUES (1, 1, 'name', 'created', 'Unknown', NOW(), 'Admin');
# These are just for testing
# INSERT INTO hardware_profiles VALUES (2, 'Dell r610', 'Dell', 'r610', 1, '#fff', NOW(), NOW(), 'Admin');
# INSERT INTO hardware_profiles VALUES (3, 'Dell r720', 'Dell', 'r720', 1, '#fff', NOW(), NOW(), 'Admin');
# INSERT INTO hardware_profiles VALUES (4, 'Sun Microsystems x4200', 'Sun Microsystems', 'x4200', 1, '#fff', NOW(), NOW(), 'Admin');
# INSERT INTO hardware_profiles VALUES (5, 'Sun Microsystems e3000', 'Sun Microsystems', 'e3000', 1, '#fff', NOW(), NOW(), 'Admin');
# INSERT INTO hardware_profiles VALUES (6, 'Citrix Xen Guest', 'Citrix', 'Xen Guest', 1, '#fff', NOW(), NOW(), 'Admin');

INSERT INTO operating_systems VALUES (1, 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', NOW(), NOW(), 'Admin');
INSERT INTO operating_systems_audit VALUES (1, 1, 'name', 'created', 'Unknown', NOW(), 'Admin');
# These are just for testing
# INSERT INTO operating_systems VALUES (3, 'CentOS 5.4 x86_64', 'CentOS', '5.4', 'x86_64', 'CentOS release 5.4', NOW(), NOW(), 'Admin');
# INSERT INTO operating_systems VALUES (4, 'CentOS 6.7 x86_64', 'CentOS', '6.7', 'x86_64', 'CentOS release 6.7', NOW(), NOW(), 'Admin');


#
# TESTING DATA
#
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (1,  'hypervisor1', 1, 3, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (2,  'hypervisor2', 2, 3, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (3,  'hypervisor3', 3, 1, 1, 1,'Admin', NOW(), NOW(), NOW());
#
# This:
# for i in `seq 4 20` ; do
#     echo "INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (${i}, 'guest_vm${i}', ${i}, 1, 1, 1,'Admin', NOW(), NOW(), NOW());"
# done
#
# Generates this:
#
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (4,  'guest_vm4',   4, 3, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (5,  'guest_vm5',   5, 3, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (6,  'guest_vm6',   6, 2, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (7,  'guest_vm7',   7, 3, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (8,  'guest_vm8',   8, 3, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (9,  'guest_vm9',   9, 1, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (10, 'guest_vm10', 10, 1, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (11, 'guest_vm11', 11, 1, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (12, 'guest_vm12', 12, 1, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (13, 'guest_vm13', 13, 1, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (14, 'guest_vm14', 14, 1, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (15, 'guest_vm15', 15, 1, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (16, 'guest_vm16', 16, 1, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (17, 'guest_vm17', 17, 1, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (18, 'guest_vm18', 18, 1, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (19, 'guest_vm19', 19, 1, 1, 1,'Admin', NOW(), NOW(), NOW());
# INSERT INTO nodes (id,name,unique_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (20, 'guest_vm20', 20, 1, 1, 1,'Admin', NOW(), NOW(), NOW());
#
# INSERT INTO hypervisor_vm_assignments (hypervisor_id,guest_vm_id) VALUES (1,4);
# INSERT INTO hypervisor_vm_assignments (hypervisor_id,guest_vm_id) VALUES (1,5);
# INSERT INTO hypervisor_vm_assignments (hypervisor_id,guest_vm_id) VALUES (1,6);
# INSERT INTO hypervisor_vm_assignments (hypervisor_id,guest_vm_id) VALUES (1,7);
# INSERT INTO hypervisor_vm_assignments (hypervisor_id,guest_vm_id) VALUES (2,8);
# INSERT INTO hypervisor_vm_assignments (hypervisor_id,guest_vm_id) VALUES (2,9);
