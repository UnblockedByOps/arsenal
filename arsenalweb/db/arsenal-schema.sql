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
  `tag_id`                 int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `tag_name`               varchar(255) COLLATE utf8_bin NOT NULL,
  `tag_value`              varchar(255) COLLATE utf8_bin NOT NULL,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_tag_id on tags (tag_id);
CREATE UNIQUE INDEX idx_uniq_tag on tags (tag_name, tag_value);

###
### TABLE: tag_node_assignments
###   This contains assignments of tags to nodes object_type.
###
DROP TABLE IF EXISTS `tag_node_assignments`;
CREATE TABLE `tag_node_assignments` (
  `tag_node_assignment_id`     int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `tag_id`                     int(11) UNSIGNED,
  `node_id`                    int(11) UNSIGNED, # to start, node_id or node_group_id
  `created`                    timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                    timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by`                 varchar(200) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_tag_node_assignment_id on tag_node_assignments (tag_node_assignment_id);
CREATE UNIQUE INDEX idx_uniq_tag_node_assignment on tag_node_assignments (tag_id, node_id);

###
### TABLE: tag_node_group_assignments
###   This contains assignments of tags to node_groups object_type.
###
DROP TABLE IF EXISTS `tag_node_group_assignments`;
CREATE TABLE `tag_node_group_assignments` (
  `tag_node_group_assignment_id`  int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `tag_id`                        int(11) UNSIGNED,
  `node_group_id`                 int(11) UNSIGNED, # to start, node_id or node_group_id
  `created`                       timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                       timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by`                    varchar(200) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_tag_node_group_assignment_id on tag_node_group_assignments (tag_node_group_assignment_id);
CREATE UNIQUE INDEX idx_uniq_tag_node_group_assignment on tag_node_group_assignments (tag_id, node_group_id);

###
### TABLE: hardware_profiles
###   This contains definitions of hardware_profiles that are associated
###   a node.
###
DROP TABLE IF EXISTS `hardware_profiles`;
CREATE TABLE `hardware_profiles` (
  `hardware_profile_id`    int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `manufacturer`           varchar(255) COLLATE utf8_bin NOT NULL,
  `model`                  varchar(255) COLLATE utf8_bin NOT NULL,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE UNIQUE INDEX idx_uniq_hardware_profile on hardware_profiles (manufacturer, model);

###
### TABLE: ip_addresses
###   This contains definitions of ip_addresses that are associated
###   a node.
###
DROP TABLE IF EXISTS `ip_addresses`;
CREATE TABLE `ip_addresses` (
  `ip_address_id`          int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `network_interface_id`   int(11) UNSIGNED,
  `address`                varchar(255) COLLATE utf8_bin,
  `address_type`           varchar(255) COLLATE utf8_bin,
  `netmask`                varchar(255) COLLATE utf8_bin,
  `broadcast`              varchar(255) COLLATE utf8_bin,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_ip_addresses_id on ip_addresses (ip_address_id);

###
### TABLE: network_interfaces
###   This contains definitions of network_interfaces that are associated
###   a node.
###
DROP TABLE IF EXISTS `network_interfaces`;
CREATE TABLE `network_interfaces` (
  `network_interface_id`    int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `network_interface_name`  varchar(255) COLLATE utf8_bin,
  `interface_type`          varchar(255) COLLATE utf8_bin,
  `physical`                tinyint(1) UNSIGNED,
  `hardware_address`        varchar(255) COLLATE utf8_bin,
  `up`                      tinyint(1) UNSIGNED,
  `link`                    tinyint(1) UNSIGNED,
  `speed`                   int(11) UNSIGNED,
  `full_duplex`             tinyint(1) UNSIGNED,
  `autonegotiate`           tinyint(1) UNSIGNED,
  `node_id`                 int(11) UNSIGNED NOT NULL,
  `created`                 timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                 timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_network_interface_id on network_interfaces (network_interface_id);

###
### TABLE: node_group_assignments
###   This contains assignments of node_groups to nodes.
###
DROP TABLE IF EXISTS `node_group_assignments`;
CREATE TABLE `node_group_assignments` (
  `node_group_assignment_id`  int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `node_id`                   int(11) UNSIGNED,
  `node_group_id`             int(11) UNSIGNED,
  `created`                   timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                   timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_node_group_assignment_id on node_group_assignments (node_group_assignment_id);

###
### TABLE: node_groups
###   The node_groups table.
###
DROP TABLE IF EXISTS `node_groups`;
CREATE TABLE `node_groups` (
  `node_group_id`          int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `node_group_name`        varchar(255) COLLATE utf8_bin NOT NULL,
  `node_group_owner`       varchar(255) COLLATE utf8_bin NOT NULL,
  `description`            text NOT NULL,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_node_group_id on node_groups (node_group_id);
CREATE UNIQUE INDEX idx_unique_node_group_name on node_groups (node_group_name);


###
### TABLE: nodes
###   The nodes table.
###
DROP TABLE IF EXISTS `nodes`;
CREATE TABLE `nodes` (
  `node_id`                           int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `node_name`                         varchar(255) COLLATE utf8_bin NOT NULL,
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
  `updated_by`                        varchar(200) COLLATE utf8_bin NOT NULL,
  `created`                           timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                           timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_node_id on nodes (node_id);
CREATE UNIQUE INDEX idx_node_ec2_id on nodes (ec2_id);

###
### TABLE: ec2
###   The ec2 table. This contains alll the ec2 facts for a given
###   node. In the future there could be more tables for various
###   cloud providers.
###
DROP TABLE IF EXISTS `ec2`;
CREATE TABLE `ec2` (
  `ec2_id`                            int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `ec2_ami_id`                        varchar(255) DEFAULT NULL,
  `ec2_hostname`                      varchar(255) DEFAULT NULL,
  `ec2_instance_id`                   varchar(255) DEFAULT NULL,
  `ec2_instance_type`                 varchar(255) DEFAULT NULL,
  `ec2_kernel_id`                     varchar(255) DEFAULT NULL,
  `ec2_local_hostname`                varchar(255) DEFAULT NULL,
  `ec2_local_ipv4`                    varchar(255) DEFAULT NULL,
  `ec2_placement_availability_zone`   varchar(255) DEFAULT NULL,
  `ec2_profile`                       varchar(255) DEFAULT NULL,
  `ec2_local_ipv4`                    varchar(255) DEFAULT NULL,
  `ec2_public_hostname`               varchar(255) DEFAULT NULL,
  `ec2_public_ipv4`                   varchar(255) DEFAULT NULL,
  `ec2_reservation_id`                varchar(255) DEFAULT NULL,
  `ec2_security_groups`               varchar(255) DEFAULT NULL,
  `created`                           timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                           timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by`                        varchar(200) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_ec2_id on ec2 (ec2_id);

###
### TABLE: statuses
###   The statuses table.
###
DROP TABLE IF EXISTS `statuses`;
CREATE TABLE `statuses` (
  `status_id`              int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `status_name`            varchar(255) COLLATE utf8_bin NOT NULL,
  `description`            text NOT NULL,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE UNIQUE INDEX idx_status_name_uniq on statuses (status_name);


###
### TABLE: operating_systems
###   The operating_systems table.
###
### FIXME: needs a unique index
###
DROP TABLE IF EXISTS `operating_systems`;
CREATE TABLE `operating_systems` (
  `operating_system_id`    int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `variant`                varchar(255) COLLATE utf8_bin NOT NULL,
  `version_number`         varchar(255) COLLATE utf8_bin NOT NULL,
  `architecture`           varchar(255) COLLATE utf8_bin NOT NULL,
  `description`            text,
  `updated_by`             varchar(200) COLLATE utf8_bin NOT NULL,
  `created`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE UNIQUE INDEX idx_operating_systems_uniq on operating_systems (variant,version_number,architecture);

###
### TABLE: hypervisor_vm_assignments
###   The hypervisor_vm_assignments table. This table maps VMs to
###   their hypervisor.
###
DROP TABLE IF EXISTS `hypervisor_vm_assignments`;
CREATE TABLE `hypervisor_vm_assignments` (
  `hypervisor_vm_assignment_id`  int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `parent_node_id`                int(11) UNSIGNED NOT NULL,
  `child_node_id`                 int(11) UNSIGNED NOT NULL,
  `updated_by`                    varchar(200) COLLATE utf8_bin NOT NULL,
  `created`                       timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated`                       timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
CREATE INDEX idx_hypervisor_vm_assignment_id on hypervisor_vm_assignments (hypervisor_vm_assignment_id);
CREATE UNIQUE INDEX idx_hypervisor_vm_assignments_uniq on hypervisor_vm_assignments (child_node_id);



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

CREATE UNIQUE INDEX idx_group_name_unique on groups (group_name);

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


