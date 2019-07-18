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

# Test hardware_profiles FIXME: Need audit entries
INSERT INTO hardware_profiles VALUES (2, 'VMware, Inc. VMware Virtual Platform', 'VMware, Inc.', 'VMware Virtual Platform', NOW(), NOW(), 'Admin');
INSERT INTO hardware_profiles VALUES (3, 'HP ProLiant DL360 Gen9', 'HP', 'ProLiant DL360 Gen9', NOW(), NOW(), 'Admin');
INSERT INTO hardware_profiles VALUES (4, 'HP ProLiant m710x Server Cartridge', 'HP', 'ProLiant m710x Server Cartridge', NOW(), NOW(), 'Admin');
INSERT INTO hardware_profiles VALUES (5, 'HP ProLiant m510 Server Cartridge', 'HP', 'ProLiant m510 Server Cartridge', NOW(), NOW(), 'Admin');
INSERT INTO hardware_profiles VALUES (6, 'Sun Microsystems e3000', 'Sun Microsystems', 'e3000', NOW(), NOW(), 'Admin');
INSERT INTO hardware_profiles VALUES (7, 'Dell Inc. PowerEdge R740xd', 'Dell Inc.', 'PowerEdge R740xd', NOW(), NOW(), 'Admin');

# Test operating_systems FIXME: Need audit entries
INSERT INTO operating_systems VALUES (2, 'CentOS 5.8 x86_64', 'CentOS', '5.8', 'x86_64', 'CentOS release 5.8 (Final)', 'Admin', NOW(), NOW());
INSERT INTO operating_systems VALUES (3, 'CentOS 6.7 x86_64', 'CentOS', '6.7', 'x86_64', 'CentOS release 6.7 (Final)', 'Admin', NOW(), NOW());
INSERT INTO operating_systems VALUES (4, 'CentOS 6.8 x86_64', 'CentOS', '6.8', 'x86_64', 'CentOS release 6.8 (Final)', 'Admin', NOW(), NOW());
INSERT INTO operating_systems VALUES (5, 'CentOS 7.2.1511 x86_64', 'CentOS', '7.2.1511', 'x86_64', 'CentOS Linux release 7.2.1511 (Core)', 'Admin', NOW(), NOW());
INSERT INTO operating_systems VALUES (6, 'CentOS 7.3.1611 x86_64', 'CentOS', '7.3.1611', 'x86_64', 'CentOS Linux release 7.3.1611 (Core)', 'Admin', NOW(), NOW());
# Test data_centers
#----------------------------------------------
INSERT INTO data_centers (id,name,created,updated,updated_by) VALUES (1, 'test_data_center_1', NOW(), NOW(), 'Admin');
INSERT INTO data_centers (id,name,created,updated,updated_by) VALUES (2, 'test_data_center_2', NOW(), NOW(), 'Admin');
INSERT INTO data_centers (id,name,created,updated,updated_by) VALUES (3, 'other_test_data_center_1', NOW(), NOW(), 'Admin');
INSERT INTO data_centers_audit VALUES (1, 1, 'name', 'created', 'test_data_center_1', 'Admin', NOW());
INSERT INTO data_centers_audit VALUES (2, 2, 'name', 'created', 'test_data_center_2', 'Admin', NOW());
INSERT INTO data_centers_audit VALUES (3, 3, 'name', 'created', 'other_test_data_center_1', 'Admin', NOW());

# Test physical_locations
#----------------------------------------------
INSERT INTO physical_locations (id,name,created,updated,updated_by) VALUES (1, 'test_physical_location_1', NOW(), NOW(), 'Admin');
INSERT INTO physical_locations (id,name,created,updated,updated_by) VALUES (2, 'test_physical_location_2', NOW(), NOW(), 'Admin');
INSERT INTO physical_locations (id,name,created,updated,updated_by) VALUES (3, 'other_test_physical_location_1', NOW(), NOW(), 'Admin');
INSERT INTO physical_locations_audit VALUES (1, 1, 'name', 'created', 'test_physical_location_1', 'Admin', NOW());
INSERT INTO physical_locations_audit VALUES (2, 2, 'name', 'created', 'test_physical_location_2', 'Admin', NOW());
INSERT INTO physical_locations_audit VALUES (3, 3, 'name', 'created', 'other_test_physical_location_1', 'Admin', NOW());

# Test physical_racks
#----------------------------------------------
INSERT INTO physical_racks (id,name,physical_location_id,created,updated,updated_by) VALUES (1, 'R900', 1, NOW(), NOW(), 'Admin');
INSERT INTO physical_racks (id,name,physical_location_id,created,updated,updated_by) VALUES (2, 'R901', 1, NOW(), NOW(), 'Admin');
INSERT INTO physical_racks (id,name,physical_location_id,created,updated,updated_by) VALUES (3, 'R900', 2, NOW(), NOW(), 'Admin');
INSERT INTO physical_racks_audit VALUES (1, 1, 'id', 'created', 1, 'Admin', NOW());
INSERT INTO physical_racks_audit VALUES (2, 2, 'id', 'created', 2, 'Admin', NOW());
INSERT INTO physical_racks_audit VALUES (3, 3, 'id', 'created', 3, 'Admin', NOW());

# Test physical_elevations
#----------------------------------------------
INSERT INTO physical_elevations (id,elevation,physical_rack_id,created,updated,updated_by) VALUES (1, 1, 1, NOW(), NOW(), 'Admin');
INSERT INTO physical_elevations (id,elevation,physical_rack_id,created,updated,updated_by) VALUES (2, 2, 1, NOW(), NOW(), 'Admin');
INSERT INTO physical_elevations (id,elevation,physical_rack_id,created,updated,updated_by) VALUES (3, 3, 1, NOW(), NOW(), 'Admin');
INSERT INTO physical_elevations (id,elevation,physical_rack_id,created,updated,updated_by) VALUES (4, 1, 2, NOW(), NOW(), 'Admin');
INSERT INTO physical_elevations (id,elevation,physical_rack_id,created,updated,updated_by) VALUES (5, 2, 2, NOW(), NOW(), 'Admin');
INSERT INTO physical_elevations (id,elevation,physical_rack_id,created,updated,updated_by) VALUES (6, 3, 2, NOW(), NOW(), 'Admin');
INSERT INTO physical_elevations (id,elevation,physical_rack_id,created,updated,updated_by) VALUES (7, 1, 3, NOW(), NOW(), 'Admin');
INSERT INTO physical_elevations (id,elevation,physical_rack_id,created,updated,updated_by) VALUES (8, 2, 3, NOW(), NOW(), 'Admin');
INSERT INTO physical_elevations (id,elevation,physical_rack_id,created,updated,updated_by) VALUES (9, 3, 3, NOW(), NOW(), 'Admin');
INSERT INTO physical_elevations_audit VALUES (1, 1, 'id', 'created', 1, 'Admin', NOW());
INSERT INTO physical_elevations_audit VALUES (1, 1, 'id', 'created', 2, 'Admin', NOW());
INSERT INTO physical_elevations_audit VALUES (1, 1, 'id', 'created', 3, 'Admin', NOW());
INSERT INTO physical_elevations_audit VALUES (1, 1, 'id', 'created', 4, 'Admin', NOW());
INSERT INTO physical_elevations_audit VALUES (1, 1, 'id', 'created', 5, 'Admin', NOW());
INSERT INTO physical_elevations_audit VALUES (1, 1, 'id', 'created', 6, 'Admin', NOW());
INSERT INTO physical_elevations_audit VALUES (1, 1, 'id', 'created', 7, 'Admin', NOW());
INSERT INTO physical_elevations_audit VALUES (1, 1, 'id', 'created', 8, 'Admin', NOW());
INSERT INTO physical_elevations_audit VALUES (1, 1, 'id', 'created', 9, 'Admin', NOW());

# Test physical_devices
#----------------------------------------------
INSERT INTO physical_devices (id,
                              serial_number,
                              physical_elevation_id,
                              physical_location_id,
                              physical_rack_id,
                              mac_address_1,
                              mac_address_2,
                              hardware_profile_id,
                              oob_ip_address,
                              oob_mac_address,
                              created,
                              updated,
                              updated_by) VALUES (1,
                                                  'Z00001', 
                                                  1, 
                                                  1, 
                                                  1, 
                                                  'aa:aa:aa:00:00:00', 
                                                  'aa:aa:aa:00:00:01', 
                                                  2, 
                                                  '10.5.5.1', 
                                                  'bb:aa:aa:00:00:00', 
                                                  NOW(),
                                                  NOW(),
                                                  'Admin');
INSERT INTO physical_devices (id,
                              serial_number,
                              physical_elevation_id,
                              physical_location_id,
                              physical_rack_id,
                              mac_address_1,
                              mac_address_2,
                              hardware_profile_id,
                              oob_ip_address,
                              oob_mac_address,
                              created,
                              updated,
                              updated_by) VALUES (2,
                                                  'Z00002', 
                                                  2, 
                                                  1, 
                                                  1, 
                                                  'aa:aa:aa:00:00:02', 
                                                  'aa:aa:aa:00:00:03', 
                                                  3, 
                                                  '10.5.5.2', 
                                                  'bb:aa:aa:00:00:01', 
                                                  NOW(),
                                                  NOW(),
                                                  'Admin');
INSERT INTO physical_devices (id,
                              serial_number,
                              physical_elevation_id,
                              physical_location_id,
                              physical_rack_id,
                              mac_address_1,
                              hardware_profile_id,
                              oob_ip_address,
                              oob_mac_address,
                              created,
                              updated,
                              updated_by) VALUES (3,
                                                  'Z00003', 
                                                  1, 
                                                  1, 
                                                  2, 
                                                  'aa:aa:aa:00:00:04', 
                                                  3, 
                                                  '10.5.5.3', 
                                                  'bb:aa:aa:00:00:02', 
                                                  NOW(),
                                                  NOW(),
                                                  'Admin');
INSERT INTO physical_devices (id,
                              serial_number,
                              physical_elevation_id,
                              physical_location_id,
                              physical_rack_id,
                              mac_address_1,
                              mac_address_2,
                              hardware_profile_id,
                              oob_ip_address,
                              oob_mac_address,
                              created,
                              updated,
                              updated_by) VALUES (4,
                                                  'Z00003', 
                                                  1, 
                                                  2, 
                                                  3, 
                                                  'aa:aa:aa:00:00:06', 
                                                  'aa:aa:aa:00:00:07', 
                                                  3, 
                                                  '10.5.5.4', 
                                                  'bb:aa:aa:00:00:03', 
                                                  NOW(),
                                                  NOW(),
                                                  'Admin');
INSERT INTO physical_devices_audit VALUES (1, 1, 'serial_number', 'created', 'Z00001', 'Admin', NOW());
INSERT INTO physical_devices_audit VALUES (2, 2, 'serial_number', 'created', 'Z00002', 'Admin', NOW());
INSERT INTO physical_devices_audit VALUES (3, 3, 'serial_number', 'created', 'Z00003', 'Admin', NOW());
INSERT INTO physical_devices_audit VALUES (4, 4, 'serial_number', 'created', 'Z00004', 'Admin', NOW());


# Test nodes
#----------------------------------------------
#
# Status id
#
# 1 = initializing
# 2 = installed
# 3 = setup
# 4 = inservice
# 5 = hibernating
# 6 = decom
# 7 = available
# 8 = broken
# 9 = maintenance
#                                                                                                                                                                          operating_system_id-----------------|
#                                                                                                                                                                          hardware_profile_id--------------|  |
#                                                                                                                                                                          status_id---------------------|  |  |
#                                                                                                                                                                          data_center_id-------------|--|  |  |
INSERT INTO nodes (id,name,unique_id,data_center_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (1,  'pup0000.docker', 'pup0000.docker_uid', 1, 4, 2, 3,'Admin', NOW(),NOW(),NOW());
INSERT INTO nodes (id,name,unique_id,data_center_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (2,  'pup0001.docker', 'pup0001.docker_uid', 1, 4, 2, 3,'Admin', NOW(),NOW(),NOW());
INSERT INTO nodes (id,name,unique_id,data_center_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (3,  'pup0002.docker', 'pup0002.docker_uid', 1, 6, 6, 2,'Admin', NOW(),NOW(),NOW());
INSERT INTO nodes (id,name,unique_id,data_center_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (4,  'cbl0000.docker', 'cbl0000.docker_uid', 1, 4, 3, 6,'Admin', NOW(),NOW(),NOW());
INSERT INTO nodes (id,name,unique_id,data_center_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (5,  'log0000.docker', 'log0000.docker_uid', 1, 4, 3, 2,'Admin', NOW(),NOW(),NOW());
INSERT INTO nodes (id,name,unique_id,data_center_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (6,  'pud0000.docker', 'pud0000.docker_uid', 1, 4, 2, 3,'Admin', NOW(),NOW(),NOW());
INSERT INTO nodes (id,name,unique_id,data_center_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (7,  'emx0000.docker', 'emx0000.docker_uid', 1, 4, 4, 3,'Admin', NOW(),NOW(),NOW());
INSERT INTO nodes (id,name,unique_id,data_center_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (8,  'bck0000.docker', 'bck0000.docker_uid', 1, 4, 7, 6,'Admin', NOW(),NOW(),NOW());
INSERT INTO nodes (id,name,unique_id,data_center_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (9,  'anr0000.docker', 'anr0000.docker_uid', 1, 4, 5, 6,'Admin', NOW(),NOW(),NOW());
INSERT INTO nodes (id,name,unique_id,data_center_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (10, 'enc0000.docker', 'enc0000.docker_uid', 1, 4, 1, 6,'Admin', NOW(),NOW(),NOW());
INSERT INTO nodes (id,name,unique_id,data_center_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (11, 'enc0001.docker', 'enc0001.docker_uid', 1, 4, 1, 6,'Admin', NOW(),NOW(),NOW());
INSERT INTO nodes (id,name,unique_id,data_center_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (12, 'enc0002.docker', 'enc0002.docker_uid', 1, 4, 1, 6,'Admin', NOW(),NOW(),NOW());
INSERT INTO nodes (id,name,unique_id,data_center_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (13, 'enc0003.docker', 'enc0003.docker_uid', 1, 4, 1, 6,'Admin', NOW(),NOW(),NOW());
INSERT INTO nodes (id,name,unique_id,data_center_id,status_id,hardware_profile_id,operating_system_id,updated_by,last_registered,created,updated) VALUES (14, 'enc0004.docker', 'enc0004.docker_uid', 2, 4, 1, 6,'Admin', NOW(),NOW(),NOW());
INSERT INTO nodes_audit VALUES (1,   1, 'name', 'created', 'pup0000.docker', 'Admin', NOW());
INSERT INTO nodes_audit VALUES (2,   2, 'name', 'created', 'pup0001.docker', 'Admin', NOW());
INSERT INTO nodes_audit VALUES (3,   3, 'name', 'created', 'pup0002.docker', 'Admin', NOW());
INSERT INTO nodes_audit VALUES (4,   4, 'name', 'created', 'cbl0000.docker', 'Admin', NOW());
INSERT INTO nodes_audit VALUES (5,   5, 'name', 'created', 'log0000.docker', 'Admin', NOW());
INSERT INTO nodes_audit VALUES (6,   6, 'name', 'created', 'pud0000.docker', 'Admin', NOW());
INSERT INTO nodes_audit VALUES (7,   7, 'name', 'created', 'emx0000.docker', 'Admin', NOW());
INSERT INTO nodes_audit VALUES (8,   8, 'name', 'created', 'bck0000.docker', 'Admin', NOW());
INSERT INTO nodes_audit VALUES (9,   9, 'name', 'created', 'anr0000.docker', 'Admin', NOW());
INSERT INTO nodes_audit VALUES (10, 10, 'name', 'created', 'enc0000.docker', 'Admin', NOW());
INSERT INTO nodes_audit VALUES (11, 11, 'name', 'created', 'enc0001.docker', 'Admin', NOW());
INSERT INTO nodes_audit VALUES (12, 12, 'name', 'created', 'enc0002.docker', 'Admin', NOW());
INSERT INTO nodes_audit VALUES (13, 13, 'name', 'created', 'enc0003.docker', 'Admin', NOW());
INSERT INTO nodes_audit VALUES (14, 14, 'name', 'created', 'enc0004.docker', 'Admin', NOW());

# Test node_groups
#----------------------------------------------
INSERT INTO node_groups VALUES (2, 'pup_docker', 'pup ops', 'Node group for regression testing in docker', 'https://some/documentation', NOW(), NOW(), 'Admin');
INSERT INTO node_groups VALUES (3, 'cbl_docker', 'cbl ops', 'Node group for regression testing in docker', 'https://some/documentation', NOW(), NOW(), 'Admin');
INSERT INTO node_groups VALUES (4, 'log_docker', 'log security', 'Node group for regression testing in docker', 'https://some/documentation', NOW(), NOW(), 'Admin');
INSERT INTO node_groups VALUES (5, 'pud_docker', 'pud ops', 'Node group for regression testing in docker', 'https://some/documentation', NOW(), NOW(), 'Admin');
INSERT INTO node_groups VALUES (6, 'emx_docker', 'emx ops', 'Node group for regression testing in docker', 'https://some/documentation', NOW(), NOW(), 'Admin');
INSERT INTO node_groups VALUES (7, 'bck_docker', 'bck ops', 'Node group for regression testing in docker', 'https://some/documentation', NOW(), NOW(), 'Admin');
INSERT INTO node_groups VALUES (8, 'enc_docker', 'enc ops', 'Node group for regression testing in docker', 'https://some/documentation', NOW(), NOW(), 'Admin');
INSERT INTO node_groups_audit VALUES (2, 2, 'name', 'created', 'pup_docker', 'Admin', NOW());
INSERT INTO node_groups_audit VALUES (3, 3, 'name', 'created', 'cbl_docker', 'Admin', NOW());
INSERT INTO node_groups_audit VALUES (4, 4, 'name', 'created', 'log_docker', 'Admin', NOW());
INSERT INTO node_groups_audit VALUES (5, 5, 'name', 'created', 'pud_docker', 'Admin', NOW());
INSERT INTO node_groups_audit VALUES (6, 6, 'name', 'created', 'emx_docker', 'Admin', NOW());
INSERT INTO node_groups_audit VALUES (7, 7, 'name', 'created', 'bck_docker', 'Admin', NOW());
INSERT INTO node_groups_audit VALUES (8, 8, 'name', 'created', 'enc_docker', 'Admin', NOW());
#
# node_group assignments
#                          node_group_id------|
#                          node_id---------|  |
INSERT INTO node_group_assignments VALUES (1, 2);
INSERT INTO node_group_assignments VALUES (2, 2);
INSERT INTO node_group_assignments VALUES (3, 2);
INSERT INTO node_group_assignments VALUES (4, 3);
INSERT INTO node_group_assignments VALUES (5, 4);
INSERT INTO node_group_assignments VALUES (6, 5);
INSERT INTO node_group_assignments VALUES (7, 6);
INSERT INTO node_group_assignments VALUES (8, 7);
INSERT INTO node_group_assignments VALUES (11, 8);
INSERT INTO node_group_assignments VALUES (12, 8);
INSERT INTO node_group_assignments VALUES (13, 8);
INSERT INTO node_group_assignments VALUES (14, 8);

# Test tags
#----------------------------------------------
INSERT INTO tags (id,name,value,updated_by,created,updated) VALUES (1,  'docker_test_tag_a',  'docker_test_1', 'Admin', NOW(),NOW());
INSERT INTO tags (id,name,value,updated_by,created,updated) VALUES (2,  'docker_test_tag_a',  'docker_test_2', 'Admin', NOW(),NOW());
INSERT INTO tags (id,name,value,updated_by,created,updated) VALUES (3,  'docker_test_tag_b',  'docker_test_1', 'Admin', NOW(),NOW());
INSERT INTO tags (id,name,value,updated_by,created,updated) VALUES (4,  'docker_test_tag_b',  'docker_test_2', 'Admin', NOW(),NOW());
INSERT INTO tags (id,name,value,updated_by,created,updated) VALUES (5,  'docker_test_tag_aa', 'docker_test_1', 'Admin', NOW(),NOW());
INSERT INTO tags (id,name,value,updated_by,created,updated) VALUES (6,  'docker_test_tag_aa', 'docker_test_2', 'Admin', NOW(),NOW());
INSERT INTO tags (id,name,value,updated_by,created,updated) VALUES (7,  'docker_test_tag_bb', 'docker_test_1', 'Admin', NOW(),NOW());
INSERT INTO tags (id,name,value,updated_by,created,updated) VALUES (8,  'docker_test_tag_bb', 'docker_test_2', 'Admin', NOW(),NOW());
INSERT INTO tags (id,name,value,updated_by,created,updated) VALUES (9,  'enc_test_tag',       'node_group_level', 'Admin', NOW(),NOW());
INSERT INTO tags (id,name,value,updated_by,created,updated) VALUES (10, 'enc_test_tag',       'data_center_level', 'Admin', NOW(),NOW());
INSERT INTO tags (id,name,value,updated_by,created,updated) VALUES (11, 'enc_test_tag',       'fqdn_level', 'Admin', NOW(),NOW());
INSERT INTO tags (id,name,value,updated_by,created,updated) VALUES (12, 'enc_test_tag_2',     'fqdn_level', 'Admin', NOW(),NOW());
INSERT INTO tags_audit VALUES (1,   1, 'name', 'created', 'docker_test_tag_a', 'Admin', NOW());
INSERT INTO tags_audit VALUES (2,   2, 'name', 'created', 'docker_test_tag_a', 'Admin', NOW());
INSERT INTO tags_audit VALUES (3,   3, 'name', 'created', 'docker_test_tag_b', 'Admin', NOW());
INSERT INTO tags_audit VALUES (4,   4, 'name', 'created', 'docker_test_tag_b', 'Admin', NOW());
INSERT INTO tags_audit VALUES (5,   5, 'name', 'created', 'docker_test_tag_aa', 'Admin', NOW());
INSERT INTO tags_audit VALUES (6,   6, 'name', 'created', 'docker_test_tag_aa', 'Admin', NOW());
INSERT INTO tags_audit VALUES (7,   7, 'name', 'created', 'docker_test_tag_bb', 'Admin', NOW());
INSERT INTO tags_audit VALUES (8,   8, 'name', 'created', 'docker_test_tag_bb', 'Admin', NOW());
INSERT INTO tags_audit VALUES (9,   9, 'name', 'created', 'enc_test_tag', 'Admin', NOW());
INSERT INTO tags_audit VALUES (10, 10, 'name', 'created', 'enc_test_tag', 'Admin', NOW());
INSERT INTO tags_audit VALUES (11, 11, 'name', 'created', 'enc_test_tag', 'Admin', NOW());
INSERT INTO tags_audit VALUES (12, 12, 'name', 'created', 'enc_test_tag_2', 'Admin', NOW());
#
# Tag node assignments
#                          node_id----------|
#                          tag_id--------|  |
INSERT INTO tag_node_assignments VALUES (1, 1);
INSERT INTO tag_node_assignments VALUES (1, 2);
INSERT INTO tag_node_assignments VALUES (1, 3);
INSERT INTO tag_node_assignments VALUES (2, 2);
INSERT INTO tag_node_assignments VALUES (2, 3);
INSERT INTO tag_node_assignments VALUES (3, 3);
INSERT INTO tag_node_assignments VALUES (3, 2);
INSERT INTO tag_node_assignments VALUES (5, 2);
INSERT INTO tag_node_assignments VALUES (6, 2);
INSERT INTO tag_node_assignments VALUES (7, 4);
INSERT INTO tag_node_assignments VALUES (8, 5);
INSERT INTO tag_node_assignments VALUES (11, 12);
INSERT INTO tag_node_assignments VALUES (12, 13);
#
# Tag node_group assignments
#                                node_group_id----|
#                                tag_id--------|  |
INSERT INTO tag_node_group_assignments VALUES (9, 8);
#
# Tag data_center assignments
#                                  data_center_id---|
#                                  tag_id--------|  |
INSERT INTO tag_data_center_assignments VALUES (10, 1);

# Test ip_addresses
#----------------------------------------------
INSERT INTO ip_addresses VALUES (1, '10.100.100.1', NOW(), NOW(), 'Admin');
INSERT INTO ip_addresses VALUES (2, '10.100.100.2', NOW(), NOW(), 'Admin');
INSERT INTO ip_addresses VALUES (3, '10.100.100.3', NOW(), NOW(), 'Admin');
INSERT INTO ip_addresses VALUES (4, '10.100.101.1', NOW(), NOW(), 'Admin');
INSERT INTO ip_addresses_audit VALUES (1, 1, 'ip_address', 'created', '10.100.100.1', 'Admin', NOW());
INSERT INTO ip_addresses_audit VALUES (2, 2, 'ip_address', 'created', '10.100.100.2', 'Admin', NOW());
INSERT INTO ip_addresses_audit VALUES (3, 3, 'ip_address', 'created', '10.100.100.3', 'Admin', NOW());
INSERT INTO ip_addresses_audit VALUES (4, 4, 'ip_address', 'created', '10.100.101.1', 'Admin', NOW());

# Test network_interfaces
#----------------------------------------------
INSERT INTO network_interfaces (id,name,unique_id,ip_address_id,created,updated,updated_by) VALUES (1, 'bond0', 'bond0_docker1', 1, NOW(), NOW(), 'Admin');
INSERT INTO network_interfaces VALUES (2, 'eth0', '00:11:22:aa:bb:cc', 1, 'bond0', 'docker_port', 'docker_port_10', 'docker_vswitch', '456', NOW(), NOW(), 'Admin');
INSERT INTO network_interfaces VALUES (3, 'eth1', '00:11:22:aa:bb:cd', 1, 'bond0', 'docker_port', 'docker_port_11', 'docker_vswitch', '456', NOW(), NOW(), 'Admin');
INSERT INTO network_interfaces VALUES (4, 'eth0', 'aa:bb:cc:00:11:22', 1, '', 'docker_port', 'docker_port_12', 'docker_vswitch', '456', NOW(), NOW(), 'Admin');
INSERT INTO network_interfaces_audit VALUES (1, 1, 'unique_id', 'created', 'bond0_docker', 'Admin', NOW());
INSERT INTO network_interfaces_audit VALUES (2, 2, 'unique_id', 'created', '00:11:22:aa:bb:cc', 'Admin', NOW());
INSERT INTO network_interfaces_audit VALUES (3, 3, 'unique_id', 'created', '00:11:22:aa:bb:cd', 'Admin', NOW());
INSERT INTO network_interfaces_audit VALUES (4, 4, 'unique_id', 'created', 'aa:bb:cc:00:11:22', 'Admin', NOW());
#
# network_interface assignments
#                   network_interface_id------|
#                   node_id----------------|  |
INSERT INTO network_interface_assignments VALUES (1, 1);
INSERT INTO network_interface_assignments VALUES (1, 2);
INSERT INTO network_interface_assignments VALUES (1, 3);
