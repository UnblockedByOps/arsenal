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
INSERT INTO users VALUES (1, 'admin@yourcompany.com', 'Nope', 'Nope', '$6$Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', 'Admin', NOW(),NOW());
# Initial kaboom password is 'password'
INSERT INTO users VALUES (2, 'kaboom', 'Register', 'Bot', '$6$Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', 'Admin', NOW(),NOW());
# Initial hvm password is 'test'
INSERT INTO users VALUES (3, 'hvm', 'Hypervisor Vm', 'Bot', '$6$MRM/VA0wb3zbpkOq', '$6$MRM/VA0wb3zbpkOq$i5GhDFjIFj9IgRmhEgxWvmt0U6VOUQp5K6XGCn/ExuieuJu8xA7Oxqc6.SVUaM0wjXgyQBw188L3ZVxolC6/m1', 'Admin', NOW(),NOW());
INSERT INTO users VALUES (4, 'aaron.bandt@citygridmedia.com', 'Aaron', 'Bandt', '$6$Vf7ZmjQarLus/TqT', '$6$Vf7ZmjQarLus/TqT$l5qsqY4ntpX8nEzbm33n5StF5D.93yV3uoh8ucthwFf8mEJBitnGLr5SWhzD2vpkpnAJnUiLl40d0hH24qPOq1', 'Admin', NOW(),NOW());

INSERT INTO groups VALUES (1,'local_admin','Admin',NOW(),NOW());
INSERT INTO groups VALUES (2,'api_write','Admin',NOW(),NOW());
INSERT INTO groups VALUES (3,'api_register','Admin',NOW(),NOW());

INSERT INTO group_perms VALUES (1,'admin',NOW(),NOW());
INSERT INTO group_perms VALUES (2,'api_write',NOW(),NOW());
INSERT INTO group_perms VALUES (3,'api_register',NOW(),NOW());

INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,1,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,2,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (2,2,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (1,3,'Admin');
INSERT INTO group_perm_assignments (group_id,perm_id,updated_by) VALUES (3,3,'Admin');

INSERT INTO local_user_group_assignments VALUES (1, 1, 1, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments VALUES (2, 2, 1, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments VALUES (3, 3, 1, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments VALUES (4, 3, 2, 'Admin', NOW(),NOW());
INSERT INTO local_user_group_assignments VALUES (5, 2, 3, 'Admin', NOW(),NOW());

INSERT INTO statuses VALUES (1, 'initializing', 'Instances in the process of spinning up.', 'Admin', NOW(),NOW());
INSERT INTO statuses VALUES (2, 'setup', 'New node, not yet configured.', 'Admin', NOW(),NOW());
INSERT INTO statuses VALUES (3, 'inservice', 'Hardware and OS functional, applications running.', 'Admin', NOW(),NOW());
INSERT INTO statuses VALUES (4, 'hibernating', 'Instances that have been spun down that will be spun up on demand.', 'Admin', NOW(),NOW());
INSERT INTO statuses VALUES (5, 'decom', 'Nodes that are dead and gone.', 'Admin', NOW(),NOW());

ALTER TABLE places ADD cs_id bigint(1) COLLATE utf8_bin NOT NULL AFTER place_id;


