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

###
### TABLE: tags
###   This contains definitions of tags which are key/value pairs that
###   are associated with a node, nodegroup or other object (examples?),
###
DROP TABLE IF EXISTS `tags`;
CREATE TABLE `tags` (
  `id`                     int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name`                   varchar(255) COLLATE utf8_bin NOT NULL,
  `value`                  varchar(255) COLLATE utf8_bin NOT NULL,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_tag_id on tags (id);
CREATE UNIQUE INDEX idx_uniq_tag on tags (name, value);

###
### TABLE: tag_node_assignments
###   This contains assignments of tags to nodes object_type.
###
DROP TABLE IF EXISTS `tag_node_assignments`;
CREATE TABLE `tag_node_assignments` (
  `tag_id`                     int(11) UNSIGNED,
  `node_id`                    int(11) UNSIGNED
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: tag_node_group_assignments
###   This contains assignments of tags to node_groups object_type.
###
DROP TABLE IF EXISTS `tag_node_group_assignments`;
CREATE TABLE `tag_node_group_assignments` (
  `tag_id`                        int(11) UNSIGNED,
  `node_group_id`                 int(11) UNSIGNED
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: tag_data_center_assignments
###   This contains assignments of tags to data_centers object_type.
###
DROP TABLE IF EXISTS `tag_data_center_assignments`;
CREATE TABLE `tag_data_center_assignments` (
  `tag_id`                        int(11) UNSIGNED,
  `data_center_id`                 int(11) UNSIGNED
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: data_centers
###   The data_centers table.
###
### Address fields based on:
### https://www.drupal.org/project/address
###
DROP TABLE IF EXISTS `data_centers`;
CREATE TABLE `data_centers` (
  `id`                     int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name`                   varchar(255) COLLATE utf8_bin NOT NULL,
  `status_id`              int(11) NOT NULL,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_data_center_id on data_centers (id);
CREATE UNIQUE INDEX idx_unique_data_center_name on data_centers (name);

###
### TABLE: hardware_profiles
###   This contains definitions of hardware_profiles that are associated
###   a node.
###
DROP TABLE IF EXISTS `hardware_profiles`;
CREATE TABLE `hardware_profiles` (
  `id`                     int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name`                   varchar(255) COLLATE utf8_bin NOT NULL,
  `manufacturer`           varchar(255) COLLATE utf8_bin NOT NULL,
  `model`                  varchar(255) COLLATE utf8_bin NOT NULL,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE UNIQUE INDEX idx_uniq_hardware_profile on hardware_profiles (name);

###
### TABLE: ip_addresses
###   The ip_addresses table.
###
DROP TABLE IF EXISTS `ip_addresses`;
CREATE TABLE `ip_addresses` (
      `id`                     int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `ip_address`             varchar(255) COLLATE utf8_bin NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE UNIQUE INDEX idx_ip_address_uniq on ip_addresses (ip_address);

###
### TABLE: network_interface_assignments
###   This contains assignments of network_interfaces to nodes.
###
DROP TABLE IF EXISTS `network_interface_assignments`;
CREATE TABLE `network_interface_assignments` (
  `node_id`                   int(11) UNSIGNED,
  `network_interface_id`      int(11) UNSIGNED
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: network_interfaces
###   This contains definitions of network_interfaces that are associated
###   to a node.
###
DROP TABLE IF EXISTS `network_interfaces`;
CREATE TABLE `network_interfaces` (
  `id`                     int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name`                   varchar(255) COLLATE utf8_bin NOT NULL,
  `unique_id`              varchar(255) COLLATE utf8_bin NOT NULL,
  `ip_address_id`          int(11),
  `bond_master`            text,
  `port_description`       text,
  `port_number`            text,
  `port_switch`            text,
  `port_vlan`              text,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_network_interface_id on network_interfaces (id);
CREATE UNIQUE INDEX idx_unique_network_interface_unique_id on network_interfaces (unique_id);

###
### TABLE: node_group_assignments
###   This contains assignments of node_groups to nodes.
###
DROP TABLE IF EXISTS `node_group_assignments`;
CREATE TABLE `node_group_assignments` (
  `node_id`                   int(11) UNSIGNED,
  `node_group_id`             int(11) UNSIGNED
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: node_groups
###   The node_groups table.
###
DROP TABLE IF EXISTS `node_groups`;
CREATE TABLE `node_groups` (
  `id`                     int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name`                   varchar(255) COLLATE utf8_bin NOT NULL,
  `owner`                  varchar(255) COLLATE utf8_bin NOT NULL,
  `description`            text NOT NULL,
  `notes_url`              text,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_node_group_id on node_groups (id);
CREATE UNIQUE INDEX idx_unique_node_group_name on node_groups (name);


###
### TABLE: nodes
###   The nodes table.
###
DROP TABLE IF EXISTS `nodes`;
CREATE TABLE `nodes` (
  `id`                                int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name`                              varchar(255) COLLATE utf8_bin NOT NULL,
  `unique_id`                         varchar(255) DEFAULT NULL,
  `status_id`                         int(11) NOT NULL,
  `serial_number`                     varchar(255) DEFAULT NULL,
  `hardware_profile_id`               int(11) DEFAULT NULL,
  `operating_system_id`               int(11) DEFAULT NULL,
  `processor_manufacturer`            varchar(255) DEFAULT NULL,
  `processor_model`                   varchar(255) DEFAULT NULL,
  `processor_speed`                   varchar(255) DEFAULT NULL,  # Questionable
  `processor_socket_count`            int(11) DEFAULT NULL,  # Questionable
  `processor_count`                   int(11) DEFAULT NULL,
  `physical_memory`                   varchar(255) DEFAULT NULL,
  `os_memory`                         varchar(255) DEFAULT NULL,
  `console_type`                      varchar(255) DEFAULT NULL,
  `kernel_version`                    varchar(255) DEFAULT NULL,
  `processor_core_count`              int(11) DEFAULT NULL,
  `os_processor_count`                int(11) DEFAULT NULL,
  `asset_tag`                         varchar(255) DEFAULT NULL,
  `timezone`                          varchar(255) DEFAULT NULL,
  `virtualarch`                       varchar(255) DEFAULT NULL,
  `uptime`                            varchar(255) DEFAULT NULL,
  `puppet_version`                    varchar(255) DEFAULT NULL,
  `facter_version`                    varchar(255) DEFAULT NULL,
  `ec2_id`                            int(11) DEFAULT NULL,
  `data_center_id`                    int(11) DEFAULT NULL,
  `updated_by`                        varchar(200) COLLATE utf8_bin NOT NULL,
  `last_registered`                   timestamp DEFAULT CURRENT_TIMESTAMP,
  `created`                           timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                           timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_node_id on nodes (id);
CREATE INDEX idx_node_name on nodes (name);
CREATE UNIQUE INDEX idx_node_ec2_id on nodes (ec2_id);

###
### TABLE: ec2_instances
###   The ec2_instances table. This contains alll the ec2 facts for a given
###   node. In the future there could be more tables for various
###   cloud providers.
###
DROP TABLE IF EXISTS `ec2_instances`;
CREATE TABLE `ec2_instances` (
  `id`                            int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `ami_id`                        varchar(255) NOT NULL,
  `hostname`                      varchar(255) NOT NULL,
  `instance_id`                   varchar(255) NOT NULL,
  `instance_type`                 varchar(255) NOT NULL,
  `availability_zone`             varchar(255) DEFAULT NULL,
  `profile`                       varchar(255) DEFAULT NULL,
  `reservation_id`                varchar(255) DEFAULT NULL,
  `security_groups`               varchar(255) DEFAULT NULL,
  `created`                       timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                       timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by`                    varchar(200) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_ec2_id on ec2_instances (id);
CREATE UNIQUE INDEX idx_ec2_instance_id on ec2_instances (instance_id);

###
### TABLE: physical_locations
###   The physical_locations table.
###
DROP TABLE IF EXISTS `physical_locations`;
CREATE TABLE `physical_locations` (
  `id`              int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name`            varchar(255) COLLATE utf8_bin NOT NULL,
  `provider`        text,
  `address_1`       text,
  `address_2`       text,
  `city`            text,
  `admin_area`      text,
  `country`         text,
  `postal_code`     text,
  `contact_name`    text,
  `phone_number`    text,
  `updated_by`      varchar(200) COLLATE utf8_bin NOT NULL,
  `created`         timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`         timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_physical_location_id on physical_locations (id);
CREATE UNIQUE INDEX idx_physical_location_name on physical_locations (name);

###
### TABLE: physical_racks
###   The physical_racks table.
###
DROP TABLE IF EXISTS `physical_racks`;
CREATE TABLE `physical_racks` (
  `id`                      int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name`                    varchar(255) NOT NULL,
  `physical_location_id`    int(11) NOT NULL,
  `updated_by`              varchar(200) COLLATE utf8_bin NOT NULL,
  `created`                 timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                 timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_physical_rack_id on physical_racks (id);
CREATE UNIQUE INDEX idx_physical_rack_location on physical_racks (name, physical_location_id);

###
### TABLE: physical_elevation
###   The physical_elevation table.
###
DROP TABLE IF EXISTS `physical_elevations`;
CREATE TABLE `physical_elevations` (
  `id`                      int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `elevation`               int(11) NOT NULL,
  `physical_rack_id`        int(11) NOT NULL,
  `updated_by`              varchar(200) COLLATE utf8_bin NOT NULL,
  `created`                 timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                 timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_physical_elevation_id on physical_elevations (id);
CREATE UNIQUE INDEX idx_physical_elevation_location on physical_elevations (elevation, physical_rack_id);

###
### TABLE: physical_devices
###   The physical_devices table.
###
DROP TABLE IF EXISTS `physical_devices`;
CREATE TABLE `physical_devices` (
  `id`                      int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `serial_number`           varchar(255) NOT NULL,
  `physical_elevation_id`   int(11) NOT NULL,
  `physical_location_id`    int(10) NOT NULL,
  `physical_rack_id`        int(10) NOT NULL,
  `mac_address_1`           varchar(255) NOT NULL,
  `mac_address_2`           varchar(255) DEFAULT NULL,
  `hardware_profile_id`     int(11) DEFAULT NULL,
  `oob_ip_address`          varchar(255) DEFAULT NULL,
  `oob_mac_address`         varchar(255) DEFAULT NULL,
  `updated_by`              varchar(200) COLLATE utf8_bin NOT NULL,
  `created`                 timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                 timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_physical_device_id on physical_devices (id);
CREATE UNIQUE INDEX idx_physical_device_serial_number on physical_devices (serial_number);
CREATE UNIQUE INDEX idx_physical_device_rack_elevation on physical_devices (physical_rack_id, physical_elevation_id);

###
### TABLE: statuses
###   The statuses table.
###
DROP TABLE IF EXISTS `statuses`;
CREATE TABLE `statuses` (
  `id`                     int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name`                   varchar(255) COLLATE utf8_bin NOT NULL,
  `description`            text NOT NULL,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE UNIQUE INDEX idx_status_name_uniq on statuses (name);


###
### TABLE: operating_systems
###   The operating_systems table.
###
DROP TABLE IF EXISTS `operating_systems`;
CREATE TABLE `operating_systems` (
  `id`                     int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name`                   varchar(255) COLLATE utf8_bin NOT NULL,
  `variant`                varchar(255) COLLATE utf8_bin NOT NULL,
  `version_number`         varchar(255) COLLATE utf8_bin NOT NULL,
  `architecture`           varchar(255) COLLATE utf8_bin NOT NULL,
  `description`            text,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE UNIQUE INDEX idx_operating_systems_uniq on operating_systems (name);

###
### TABLE: hypervisor_vm_assignments
###   This contains assignments of hypervisors to guest_vms object_type.
###
DROP TABLE IF EXISTS `hypervisor_vm_assignments`;
CREATE TABLE `hypervisor_vm_assignments` (
  `hypervisor_id`               int(11) UNSIGNED,
  `guest_vm_id`                 int(11) UNSIGNED
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

### User and groups tables

###
### TABLE: users
###   This is the local users table for installs that do not
###   wish to use AD/LDAP
###
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `user_id`                mediumint(9) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_name`              varchar(250) COLLATE utf8_bin NOT NULL,
  `first_name`             varchar(250) COLLATE utf8_bin,
  `last_name`              varchar(250) COLLATE utf8_bin,
  `salt`                   varchar(50) COLLATE utf8_bin NOT NULL,
  `password`               varchar(250) COLLATE utf8_bin NOT NULL,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE UNIQUE INDEX idx_user_name_unique on users (user_name);

###
### TABLE: groups
###   This is the primary groups table.
###
DROP TABLE IF EXISTS `groups`;
CREATE TABLE `groups` (
  `group_id`               mediumint(9) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `group_name`             varchar(250) COLLATE utf8_bin NOT NULL,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE UNIQUE INDEX idx_group_name_unique on arsenal.groups (group_name);

###
### TABLE: local_user_group_assignments
###   This table assigns local users to groups.
###
DROP TABLE IF EXISTS `local_user_group_assignments`;
CREATE TABLE `local_user_group_assignments` (
  `user_group_assignment_id`    mediumint(9) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `group_id`                    mediumint(9) UNSIGNED NOT NULL,
  `user_id`                     mediumint(9) UNSIGNED NOT NULL,
  `updated_by`                  varchar(200) COLLATE utf8_bin NOT NULL,
  `created`                     timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                     timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: group_permissions
###   This is the reference table for the list of permissions.
###
DROP TABLE IF EXISTS `group_perms`;
CREATE TABLE `group_perms` (
  `perm_id`                mediumint(9) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `perm_name`               varchar(250) COLLATE utf8_bin NOT NULL ,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE UNIQUE INDEX idx_group_perms_unique on group_perms (perm_name);

###
### TABLE: group_perm_assignments
###   This table assigns groups to permissions, controlling
###   what group memebers are able to do in the interface.
###
DROP TABLE IF EXISTS `group_perm_assignments`;
CREATE TABLE `group_perm_assignments` (
  `group_assignment_id`    mediumint(9) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `group_id`               mediumint(9) UNSIGNED NOT NULL,
  `perm_id`                mediumint(9) UNSIGNED NOT NULL,
  `updated_by`             varchar(30) NOT NULL, # this could be/become a FK
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### AUDIT TABLES
###

###
### TABLE: data_centers_audit
###   This table tracks additions, changes and deletions to the data_centers table.
###
DROP TABLE IF EXISTS `data_centers_audit`;
CREATE TABLE `data_centers_audit` (
      `id`                     bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `object_id`              int(11) UNSIGNED NOT NULL,
      `field`                  varchar(255) NOT NULL,
      `old_value`              varchar(255) NOT NULL,
      `new_value`              varchar(255) NOT NULL,
      `updated_by`             varchar(255) NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: ec2_instances_audit
###   This table tracks additions, changes and deletions to the ec2_instances table.
###
DROP TABLE IF EXISTS `ec2_instances_audit`;
CREATE TABLE `ec2_instances_audit` (
      `id`                     bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `object_id`              int(11) UNSIGNED NOT NULL,
      `field`                  varchar(255) NOT NULL,
      `old_value`              varchar(255) NOT NULL,
      `new_value`              varchar(255) NOT NULL,
      `updated_by`             varchar(255) NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: ip_addresses_audit
###   This table tracks additions, changes and deletions to the ip_addresses table.
###
DROP TABLE IF EXISTS `ip_addresses_audit`;
CREATE TABLE `ip_addresses_audit` (
      `id`                     bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `object_id`              int(11) UNSIGNED NOT NULL,
      `field`                  varchar(255) NOT NULL,
      `old_value`              varchar(255) NOT NULL,
      `new_value`              varchar(255) NOT NULL,
      `updated_by`             varchar(255) NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: nodes_audit
###   This table tracks additions, changes and deletions to the nodes table.
###
DROP TABLE IF EXISTS `nodes_audit`;
CREATE TABLE `nodes_audit` (
      `id`                     bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `object_id`              int(11) UNSIGNED NOT NULL,
      `field`                  varchar(255) NOT NULL,
      `old_value`              varchar(255) NOT NULL,
      `new_value`              varchar(255) NOT NULL,
      `updated_by`             varchar(255) NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: node_groups_audit
###   This table tracks additions, changes and deletions to the node_groups table.
###
DROP TABLE IF EXISTS `node_groups_audit`;
CREATE TABLE `node_groups_audit` (
      `id`                     bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `object_id`              int(11) UNSIGNED NOT NULL,
      `field`                  varchar(255) NOT NULL,
      `old_value`              varchar(255) NOT NULL,
      `new_value`              varchar(255) NOT NULL,
      `updated_by`             varchar(255) NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: operating_systems_audit
###   This table tracks additions, changes and deletions to the operating_systems table.
###
DROP TABLE IF EXISTS `operating_systems_audit`;
CREATE TABLE `operating_systems_audit` (
      `id`                     bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `object_id`              int(11) UNSIGNED NOT NULL,
      `field`                  varchar(255) NOT NULL,
      `old_value`              varchar(255) NOT NULL,
      `new_value`              varchar(255) NOT NULL,
      `updated_by`             varchar(255) NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: hardware_profiles_audit
###   This table tracks additions, changes and deletions to the hardware_profiles table.
###
DROP TABLE IF EXISTS `hardware_profiles_audit`;
CREATE TABLE `hardware_profiles_audit` (
      `id`                     bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `object_id`              int(11) UNSIGNED NOT NULL,
      `field`                  varchar(255) NOT NULL,
      `old_value`              varchar(255) NOT NULL,
      `new_value`              varchar(255) NOT NULL,
      `updated_by`             varchar(255) NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: statuses_audit
###   This table tracks additions, changes and deletions to the statuses table.
###
DROP TABLE IF EXISTS `statuses_audit`;
CREATE TABLE `statuses_audit` (
      `id`                     bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `object_id`              int(11) UNSIGNED NOT NULL,
      `field`                  varchar(255) NOT NULL,
      `old_value`              varchar(255) NOT NULL,
      `new_value`              varchar(255) NOT NULL,
      `updated_by`             varchar(255) NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: tags_audit
###   This table tracks additions, changes and deletions to the tags table.
###
DROP TABLE IF EXISTS `tags_audit`;
CREATE TABLE `tags_audit` (
      `id`                     bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `object_id`              int(11) UNSIGNED NOT NULL,
      `field`                  varchar(255) NOT NULL,
      `old_value`              varchar(255) NOT NULL,
      `new_value`              varchar(255) NOT NULL,
      `updated_by`             varchar(255) NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: network_interfaces_audit
###   This table tracks additions, changes and deletions to the network_interfaces table.
###
DROP TABLE IF EXISTS `network_interfaces_audit`;
CREATE TABLE `network_interfaces_audit` (
      `id`                     bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `object_id`              int(11) UNSIGNED NOT NULL,
      `field`                  varchar(255) NOT NULL,
      `old_value`              varchar(255) NOT NULL,
      `new_value`              varchar(255) NOT NULL,
      `updated_by`             varchar(255) NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: physical_locations_audit
###   This table tracks additions, changes and deletions to the physical_locations table.
###
DROP TABLE IF EXISTS `physical_locations_audit`;
CREATE TABLE `physical_locations_audit` (
      `id`                     bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `object_id`              int(11) UNSIGNED NOT NULL,
      `field`                  varchar(255) NOT NULL,
      `old_value`              varchar(255) NOT NULL,
      `new_value`              varchar(255) NOT NULL,
      `updated_by`             varchar(255) NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: physical_racks_audit
###   This table tracks additions, changes and deletions to the physical_racks table.
###
DROP TABLE IF EXISTS `physical_racks_audit`;
CREATE TABLE `physical_racks_audit` (
      `id`                     bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `object_id`              int(11) UNSIGNED NOT NULL,
      `field`                  varchar(255) NOT NULL,
      `old_value`              varchar(255) NOT NULL,
      `new_value`              varchar(255) NOT NULL,
      `updated_by`             varchar(255) NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: physical_elevations_audit
###   This table tracks additions, changes and deletions to the physical_elevations table.
###
DROP TABLE IF EXISTS `physical_elevations_audit`;
CREATE TABLE `physical_elevations_audit` (
      `id`                     bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `object_id`              int(11) UNSIGNED NOT NULL,
      `field`                  varchar(255) NOT NULL,
      `old_value`              varchar(255) NOT NULL,
      `new_value`              varchar(255) NOT NULL,
      `updated_by`             varchar(255) NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

###
### TABLE: physical_devices_audit
###   This table tracks additions, changes and deletions to the physical_devices table.
###
DROP TABLE IF EXISTS `physical_devices_audit`;
CREATE TABLE `physical_devices_audit` (
      `id`                     bigint(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `object_id`              int(11) UNSIGNED NOT NULL,
      `field`                  varchar(255) NOT NULL,
      `old_value`              varchar(255) NOT NULL,
      `new_value`              varchar(255) NOT NULL,
      `updated_by`             varchar(255) NOT NULL,
      `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
