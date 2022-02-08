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
#
# GROUPS
#
# database groups
###########################################################################
INSERT INTO groups VALUES (1, 'local_admin',               NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (2, 'api_write',                 NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (3, 'api_register',              NOW(), NOW(), 'Admin');
# Set this to whatever system group you want to have admin access (wheel, arsenal_admins, etc.)
INSERT INTO groups VALUES (4, 'arsenal_admins',            NOW(), NOW(), 'Admin');
# For devel on mac
# INSERT INTO groups VALUES (5, 'admin',                     NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (6, 'node_write',                NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (7, 'node_delete',               NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (8, 'node_group_write',          NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (9, 'node_group_delete',         NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (10,'tag_write',                 NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (11,'tag_delete',                NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (12,'data_center_write',         NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (13,'data_center_delete',        NOW(), NOW(), 'Admin');
# This is a special local group that is not assigned any permissions via route, but
# members of this group will be able to write secure tags.
INSERT INTO groups VALUES (14,'secure_tags',               NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (15,'physical_device_write',     NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (16,'physical_device_delete',    NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (17,'physical_location_write',   NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (18,'physical_location_delete',  NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (19,'physical_rack_write',       NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (20,'physical_rack_delete',      NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (21,'physical_elevation_write',  NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (22,'physical_elevation_delete', NOW(), NOW(), 'Admin');
INSERT INTO groups VALUES (23,'status_write',              NOW(), NOW(), 'Admin');

# Group permissions that can be assigned to groups
###########################################################################
INSERT INTO group_perms VALUES (1,'admin',                      NOW());
INSERT INTO group_perms VALUES (2,'api_write',                  NOW());
INSERT INTO group_perms VALUES (3,'api_register',               NOW());
INSERT INTO group_perms VALUES (4,'node_write',                 NOW());
INSERT INTO group_perms VALUES (5,'node_delete',                NOW());
INSERT INTO group_perms VALUES (6,'node_group_write',           NOW());
INSERT INTO group_perms VALUES (7,'node_group_delete',          NOW());
INSERT INTO group_perms VALUES (8,'tag_write',                  NOW());
INSERT INTO group_perms VALUES (9,'tag_delete',                 NOW());
INSERT INTO group_perms VALUES (10,'data_center_write',         NOW());
INSERT INTO group_perms VALUES (11,'data_center_delete',        NOW());
INSERT INTO group_perms VALUES (12,'physical_device_write',     NOW());
INSERT INTO group_perms VALUES (13,'physical_device_delete',    NOW());
INSERT INTO group_perms VALUES (14,'physical_location_write',   NOW());
INSERT INTO group_perms VALUES (15,'physical_location_delete',  NOW());
INSERT INTO group_perms VALUES (16,'physical_rack_write',       NOW());
INSERT INTO group_perms VALUES (17,'physical_rack_delete',      NOW());
INSERT INTO group_perms VALUES (18,'physical_elevation_write',  NOW());
INSERT INTO group_perms VALUES (19,'physical_elevation_delete', NOW());
INSERT INTO group_perms VALUES (20,'status_write',              NOW());

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
#  node_group_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (9,7);
#  tag_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (10,8);
#  tag_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (11,9);
#  data_center_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (12,10);
#  data_center_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (13,11);
#  physical_device_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (15,12);
#  physical_device_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (16,13);
#  physical_location_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (17,14);
#  physical_location_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (18,15);
#  physical_rack_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (19,16);
#  physical_rack_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (20,17);
#  physical_elevation_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (21,18);
#  physical_elevation_delete
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (22,19);
#  status_write
INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (23,20);



# For devel on mac
# INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (5,1);
# INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (5,2);
# INSERT INTO group_perm_assignments (group_id,perm_id) VALUES (5,3);

# Adding db users to db groups.
###########################################################################
### Becasue we need to allow kaboom to update status, any user added 
### to the api_write group also needs ot be added to the api_register group.
# admin           = 1
# kaboom          = 2
# hvm             = 3
# readonly        = 4
# jenkins-techops = 5
# puppet-enc      = 6
# Add user: local_admin to groups: local_admin
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (1, 1);
# Add user: hvm to groups: api_register, status_write
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (3, 2);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (3, 23);
# Add user: jenkins-techops to groups: api_write, api_regip_delete, tag_a_center_write, data_center_delete, secure_tags, physical_*, status_write
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 2);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 3);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 6);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 7);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 8);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 9);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 10);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 11);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 12);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 13);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 14);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 15);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 16);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 17);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 18);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 19);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 20);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 21);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 22);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (5, 23);
# Add user: kaboom to groups: api_register, node_write, status_write
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (2, 3);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (2, 6);
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (2, 23);
# Add user: puppet-enc to groups: node_write
INSERT INTO local_user_group_assignments (user_id,group_id) VALUES (6, 6);

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

INSERT INTO node_groups VALUES (1, 'default_install', 'admin@rubiconproject.com', 'Default node group for all nodes.', 'Documentation url', NOW(), NOW(), 'Admin');
INSERT INTO node_groups_audit VALUES (1, 1, 'name', 'created', 'default_install', NOW(), 'Admin');

INSERT INTO hardware_profiles VALUES (1, 'Unknown', 'Unknown', 'Unknown', 1, '#fff', NOW(), NOW(), 'Admin');
INSERT INTO hardware_profiles_audit VALUES (1, 1, 'name', 'created', 'Unknown', NOW(), 'Admin');

INSERT INTO operating_systems VALUES (1, 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', NOW(), NOW(), 'Admin');
INSERT INTO operating_systems_audit VALUES (1, 1, 'name', 'created', 'Unknown', NOW(), 'Admin');
