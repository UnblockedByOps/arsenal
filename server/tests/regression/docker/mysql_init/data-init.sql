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
INSERT INTO users VALUES (1, 'admin', 'Admin', 'Superuser', 'Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', 'Admin', NOW(),NOW());
# Initial kaboom password is 'password'
INSERT INTO users VALUES (2, 'kaboom', 'Register', 'Bot', 'Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', 'Admin', NOW(),NOW());
# Initial hvm password is 'test'
INSERT INTO users VALUES (3, 'hvm', 'Hypervisor Vm', 'Bot', 'MRM/VA0wb3zbpkOq', '$6$rounds=656000$MRM/VA0wb3zbpkOq$i5GhDFjIFj9IgRmhEgxWvmt0U6VOUQp5K6XGCn/ExuieuJu8xA7Oxqc6.SVUaM0wjXgyQBw188L3ZVxolC6/m1', 'Admin', NOW(),NOW());
# Initial readonly password is 'readonly'
INSERT INTO users VALUES (4, 'readonly', 'Readonly', 'User', 'AT4beMbzo1zYZRFN', '$6$rounds=656000$AT4beMbzo1zYZRFN$VbEbyjQUY7xdlHALvD.0DoN9ZhyGNR89iMRI.03BwlW9bi1b3msegIThlmo0M1yZpy3jNagdXpjZhk3/sXWSB0', 'Admin', NOW(),NOW());
# Initial jenkins-techops password is 'password'
INSERT INTO users VALUES (5, 'jenkins-techops', 'jenkins-techops', 'Bot', 'Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', 'Admin', NOW(),NOW());
# Initial puppet-enc password is 'password'
INSERT INTO users VALUES (6, 'puppet-enc', 'Puppet Node Classifier', 'Bot', 'Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', 'Admin', NOW(),NOW());
#
# GROUPS
#
# database groups
###########################################################################
INSERT INTO arsenal.groups VALUES (1,'local_admin','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (2,'api_write','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (3,'api_register','Admin',NOW(),NOW());
# Set this to whatever system group you want to have admin access (wheel, arsenal_admins, etc.)
INSERT INTO arsenal.groups VALUES (4,'arsenal_admins','Admin',NOW(),NOW());
# For devel on mac
# INSERT INTO arsenal.groups VALUES (5,'admin','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (6,'node_write','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (7,'node_delete','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (8,'node_group_write','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (9,'node_group_delete','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (10,'tag_write','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (11,'tag_delete','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (12,'data_center_write','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (13,'data_center_delete','Admin',NOW(),NOW());
# This is a special local group that is not assigned any permissions via route, but
# members of this group will be able to write secure tags.
INSERT INTO arsenal.groups VALUES (14,'secure_tags','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (14,'physical_device_write','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (15,'physical_device_delete','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (17,'physical_location_write','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (18,'physical_location_delete','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (19,'physical_rack_write','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (20,'physical_rack_delete','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (21,'physical_elevation_write','Admin',NOW(),NOW());
INSERT INTO arsenal.groups VALUES (22,'physical_elevation_delete','Admin',NOW(),NOW());


# Group permissions that can be assigned to groups
###########################################################################
INSERT INTO group_perms VALUES (1,'admin',NOW(),NOW());
INSERT INTO group_perms VALUES (2,'api_write',NOW(),NOW());
INSERT INTO group_perms VALUES (3,'api_register',NOW(),NOW());
INSERT INTO group_perms VALUES (4,'node_write',NOW(),NOW());
INSERT INTO group_perms VALUES (5,'node_delete',NOW(),NOW());
INSERT INTO group_perms VALUES (6,'node_group_write',NOW(),NOW());
INSERT INTO group_perms VALUES (7,'node_group_delete',NOW(),NOW());
INSERT INTO group_perms VALUES (8,'tag_write',NOW(),NOW());
INSERT INTO group_perms VALUES (9,'tag_delete',NOW(),NOW());
INSERT INTO group_perms VALUES (10,'data_center_write',NOW(),NOW());
INSERT INTO group_perms VALUES (11,'data_center_delete',NOW(),NOW());
INSERT INTO group_perms VALUES (12,'physical_device_write',NOW(),NOW());
INSERT INTO group_perms VALUES (13,'physical_device_delete',NOW(),NOW());
INSERT INTO group_perms VALUES (14,'physical_location_write',NOW(),NOW());
INSERT INTO group_perms VALUES (15,'physical_location_delete',NOW(),NOW());
INSERT INTO group_perms VALUES (16,'physical_rack_write',NOW(),NOW());
INSERT INTO group_perms VALUES (17,'physical_rack_delete',NOW(),NOW());
INSERT INTO group_perms VALUES (18,'physical_elevation_write',NOW(),NOW());
INSERT INTO group_perms VALUES (19,'physical_elevation_delete',NOW(),NOW());

# Assigning group permissions to groups
###########################################################################
#  local_admin gets all perms
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,1,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,2,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,3,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,4,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,5,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,6,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,7,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,8,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,9,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,10,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,11,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,12,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,13,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,14,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,15,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,16,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,17,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,18,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,19,'Admin');
#  api_write
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (2,2,'Admin');
#  api_register
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (3,3,'Admin');
#  arsenal_admins (system admin) gets all perms
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,1,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,2,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,3,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,4,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,5,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,6,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,7,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,8,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,9,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,10,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,11,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,12,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,13,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,14,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,15,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,16,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,17,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,18,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (4,19,'Admin');

#  node_write
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (6,4,'Admin');
#  node_delete
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (7,5,'Admin');
#  node_group_write
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (8,6,'Admin');
#  node_group_delete
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (9,7,'Admin');
#  tag_write
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (10,8,'Admin');
#  tag_delete
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (11,9,'Admin');
#  data_center_write
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (12,10,'Admin');
#  data_center_delete
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (13,11,'Admin');
#  physical_device_write
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (15,12,'Admin');
#  physical_device_delete
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (16,13,'Admin');
#  physical_location_write
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (17,14,'Admin');
#  physical_location_delete
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (18,15,'Admin');
#  physical_rack_write
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (19,16,'Admin');
#  physical_rack_delete
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (20,17,'Admin');
#  physical_elevation_write
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (21,18,'Admin');
#  physical_elevation_delete
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (22,19,'Admin');



# For devel on mac
# INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (5,1,'Admin');
# INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (5,2,'Admin');
# INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (5,3,'Admin');

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
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (1, 1, 'Admin', NOW(),NOW());
# Add user: hvm to groups: api_register
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (2, 3, 'Admin', NOW(),NOW());
# Add user: jenkins-techops to groups: api_write, api_register, node_write, node_group_delete, tag_write, tag_delete, data_center_write, data_center_delete, secure_tags
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (2, 5, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (3, 5, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (6, 5, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (7, 5, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (8, 5, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (9, 5, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (10, 5, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (11, 5, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (12, 5, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (13, 5, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (14, 5, 'Admin', NOW(),NOW());
# Add user: kaboom to groups: api_register, node_write
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (3, 2, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (6, 2, 'Admin', NOW(),NOW());
# Add user: puppet-enc to groups: node_write
INSERT INTO local_user_group_assignments (group_id,user_id,updated_by,created,updated) VALUES (6, 6, 'Admin', NOW(),NOW());

#
# STATUSES
#
INSERT INTO statuses VALUES (1, 'initializing', 'Instances in the process of spinning up.', 'Admin', NOW(),NOW());
INSERT INTO statuses_audit VALUES (1, 1, 'name', 'created', 'initializing', 'Admin', NOW());
INSERT INTO statuses VALUES (2, 'installed', 'New node with OS installed and base configuration applied.', 'Admin', NOW(),NOW());
INSERT INTO statuses_audit VALUES (2, 2, 'name', 'created', 'installed', 'Admin', NOW());
INSERT INTO statuses VALUES (3, 'setup', 'New node fully configured and awaiting production deployment.', 'Admin', NOW(),NOW());
INSERT INTO statuses_audit VALUES (3, 3, 'name', 'created', 'setup', 'Admin', NOW());
INSERT INTO statuses VALUES (4, 'inservice', 'Hardware and OS functional, applications running.', 'Admin', NOW(),NOW());
INSERT INTO statuses_audit VALUES (4, 4, 'name', 'created', 'inservice', 'Admin', NOW());
INSERT INTO statuses VALUES (5, 'hibernating', 'Instances that have been spun down that will be spun up on demand.', 'Admin', NOW(),NOW());
INSERT INTO statuses_audit VALUES (5, 5, 'name', 'created', 'hibernating', 'Admin', NOW());
INSERT INTO statuses VALUES (6, 'decom', 'Nodes that are dead and gone.', 'Admin', NOW(),NOW());
INSERT INTO statuses_audit VALUES (6, 6, 'name', 'created', 'decom', 'Admin', NOW());
INSERT INTO statuses VALUES (7, 'available', 'Hardware that is available to be re-purposed.', 'Admin', NOW(),NOW());
INSERT INTO statuses_audit VALUES (7, 7, 'name', 'created', 'available', 'Admin', NOW());
INSERT INTO statuses VALUES (8, 'broken', 'Hardware that is in need of repair.', 'Admin', NOW(),NOW());
INSERT INTO statuses_audit VALUES (8, 8, 'name', 'created', 'broken', 'Admin', NOW());
INSERT INTO statuses VALUES (9, 'maintenance', 'Hardware that is currently undergoing maintenance.', 'Admin', NOW(),NOW());
INSERT INTO statuses_audit VALUES (9, 9, 'name', 'created', 'maintenance', 'Admin', NOW());

INSERT INTO node_groups VALUES (1, 'default_install', 'admin@rubiconproject.com', 'Default node group for all nodes.', 'Documentation url', NOW(), NOW(), 'Admin');
INSERT INTO node_groups_audit VALUES (1, 1, 'name', 'created', 'default_install', 'Admin', NOW());

INSERT INTO hardware_profiles VALUES (1, 'Unknown', 'Unknown', 'Unknown', NOW(), NOW(), 'Admin');
INSERT INTO hardware_profiles_audit VALUES (1, 1, 'name', 'created', 'Unknown', 'Admin', NOW());

INSERT INTO operating_systems VALUES (1, 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Admin', NOW(), NOW());
INSERT INTO operating_systems_audit VALUES (1, 1, 'name', 'created', 'Unknown', 'Admin', NOW());
