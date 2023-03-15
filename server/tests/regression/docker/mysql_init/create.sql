use arsenal;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> b1bf5df56a22

CREATE TABLE data_centers_audit (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    object_id INTEGER NOT NULL, 
    field TEXT NOT NULL, 
    old_value TEXT NOT NULL, 
    new_value TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_data_centers_audit PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE ec2_instances (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    account_id VARCHAR(255) NOT NULL, 
    ami_id VARCHAR(255) NOT NULL, 
    hostname VARCHAR(255) NOT NULL, 
    instance_id VARCHAR(255) NOT NULL, 
    instance_type VARCHAR(255) NOT NULL, 
    availability_zone VARCHAR(255) NOT NULL, 
    profile VARCHAR(255) NOT NULL, 
    reservation_id VARCHAR(255) NOT NULL, 
    security_groups VARCHAR(255) NOT NULL, 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_ec2_instances PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE INDEX idx_ec2_id ON ec2_instances (id);

CREATE UNIQUE INDEX idx_ec2_instance_id ON ec2_instances (instance_id);

CREATE TABLE ec2_instances_audit (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    object_id INTEGER NOT NULL, 
    field TEXT NOT NULL, 
    old_value TEXT NOT NULL, 
    new_value TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_ec2_instances_audit PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE group_perms (
    id MEDIUMINT(9) UNSIGNED NOT NULL AUTO_INCREMENT, 
    name TEXT NOT NULL, 
    created TIMESTAMP NOT NULL, 
    CONSTRAINT pk_group_perms PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE UNIQUE INDEX idx_group_perms_unique ON group_perms (name(255));

CREATE TABLE `groups` (
    id MEDIUMINT(9) UNSIGNED NOT NULL AUTO_INCREMENT, 
    name TEXT NOT NULL, 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_groups PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE UNIQUE INDEX idx_group_name_unique ON `groups` (name(255));

CREATE TABLE hardware_profiles (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    name VARCHAR(255) NOT NULL, 
    model VARCHAR(255) NOT NULL, 
    manufacturer VARCHAR(255) NOT NULL, 
    rack_u INTEGER NOT NULL, 
    rack_color TEXT NOT NULL, 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_hardware_profiles PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE INDEX idx_hardware_profile_id ON hardware_profiles (id);

CREATE UNIQUE INDEX idx_uniq_hardware_profile ON hardware_profiles (name);

CREATE TABLE hardware_profiles_audit (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    object_id INTEGER NOT NULL, 
    field TEXT NOT NULL, 
    old_value TEXT NOT NULL, 
    new_value TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_hardware_profiles_audit PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE ip_addresses (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    ip_address VARCHAR(255) NOT NULL, 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_ip_addresses PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE UNIQUE INDEX idx_ip_address_uniq ON ip_addresses (ip_address);

CREATE TABLE ip_addresses_audit (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    object_id INTEGER NOT NULL, 
    field TEXT NOT NULL, 
    old_value TEXT NOT NULL, 
    new_value TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_ip_addresses_audit PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE network_interfaces_audit (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    object_id INTEGER NOT NULL, 
    field TEXT NOT NULL, 
    old_value TEXT NOT NULL, 
    new_value TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_network_interfaces_audit PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE node_groups (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    name VARCHAR(255) NOT NULL, 
    owner VARCHAR(255) NOT NULL, 
    description TEXT NOT NULL, 
    notes_url TEXT, 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_node_groups PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE INDEX idx_node_group_id ON node_groups (id);

CREATE UNIQUE INDEX idx_unique_node_group_name ON node_groups (name);

CREATE TABLE node_groups_audit (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    object_id INTEGER NOT NULL, 
    field TEXT NOT NULL, 
    old_value TEXT NOT NULL, 
    new_value TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_node_groups_audit PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE nodes_audit (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    object_id INTEGER NOT NULL, 
    field TEXT NOT NULL, 
    old_value TEXT NOT NULL, 
    new_value TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_nodes_audit PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE operating_systems (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    name VARCHAR(255) NOT NULL, 
    variant VARCHAR(255) NOT NULL, 
    version_number VARCHAR(255) NOT NULL, 
    architecture VARCHAR(255) NOT NULL, 
    description TEXT NOT NULL, 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_operating_systems PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE INDEX idx_operating_systems_id ON operating_systems (id);

CREATE UNIQUE INDEX idx_operating_systems_uniq ON operating_systems (name);

CREATE TABLE operating_systems_audit (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    object_id INTEGER NOT NULL, 
    field TEXT NOT NULL, 
    old_value TEXT NOT NULL, 
    new_value TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_operating_systems_audit PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE physical_devices_audit (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    object_id INTEGER NOT NULL, 
    field TEXT NOT NULL, 
    old_value TEXT NOT NULL, 
    new_value TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_physical_devices_audit PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE physical_elevations_audit (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    object_id INTEGER NOT NULL, 
    field TEXT NOT NULL, 
    old_value TEXT NOT NULL, 
    new_value TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_physical_elevations_audit PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE physical_locations (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    name VARCHAR(255) NOT NULL, 
    provider TEXT, 
    address_1 TEXT, 
    address_2 TEXT, 
    city TEXT, 
    admin_area TEXT, 
    country TEXT, 
    postal_code TEXT, 
    contact_name TEXT, 
    phone_number TEXT, 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_physical_locations PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE INDEX idx_physical_location_id ON physical_locations (id);

CREATE UNIQUE INDEX idx_physical_location_name ON physical_locations (name);

CREATE TABLE physical_locations_audit (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    object_id INTEGER NOT NULL, 
    field TEXT NOT NULL, 
    old_value TEXT NOT NULL, 
    new_value TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_physical_locations_audit PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE physical_racks_audit (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    object_id INTEGER NOT NULL, 
    field TEXT NOT NULL, 
    old_value TEXT NOT NULL, 
    new_value TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_physical_racks_audit PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE statuses (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    name VARCHAR(255) NOT NULL, 
    description TEXT NOT NULL, 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_statuses PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE INDEX idx_status_name_id ON statuses (id);

CREATE UNIQUE INDEX idx_status_name_uniq ON statuses (name);

CREATE TABLE statuses_audit (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    object_id INTEGER NOT NULL, 
    field TEXT NOT NULL, 
    old_value TEXT NOT NULL, 
    new_value TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_statuses_audit PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE tags (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    name VARCHAR(255) NOT NULL, 
    value VARCHAR(255) NOT NULL, 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_tags PRIMARY KEY (id), 
    CONSTRAINT idx_uniq_tag UNIQUE (name, value)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE INDEX idx_tag_id ON tags (id);

CREATE TABLE tags_audit (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    object_id INTEGER NOT NULL, 
    field TEXT NOT NULL, 
    old_value TEXT NOT NULL, 
    new_value TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_tags_audit PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE users (
    id MEDIUMINT(9) UNSIGNED NOT NULL AUTO_INCREMENT, 
    name TEXT NOT NULL, 
    first_name TEXT, 
    last_name TEXT, 
    salt TEXT NOT NULL, 
    password TEXT NOT NULL, 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_users PRIMARY KEY (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE UNIQUE INDEX idx_user_name_unique ON users (name(255));

CREATE TABLE data_centers (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    name VARCHAR(255) NOT NULL, 
    status_id INTEGER UNSIGNED NOT NULL, 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_data_centers PRIMARY KEY (id), 
    CONSTRAINT fk_data_centers_status_id_statuses FOREIGN KEY(status_id) REFERENCES statuses (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE INDEX idx_data_center_id ON data_centers (id);

CREATE UNIQUE INDEX idx_unique_data_center_name ON data_centers (name);

CREATE TABLE group_perm_assignments (
    group_id MEDIUMINT(9) UNSIGNED, 
    perm_id MEDIUMINT(9) UNSIGNED, 
    CONSTRAINT fk_group_perm_assignments_group_id_groups FOREIGN KEY(group_id) REFERENCES `groups` (id), 
    CONSTRAINT fk_group_perm_assignments_perm_id_group_perms FOREIGN KEY(perm_id) REFERENCES group_perms (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE local_user_group_assignments (
    user_id MEDIUMINT(9) UNSIGNED, 
    group_id MEDIUMINT(9) UNSIGNED, 
    CONSTRAINT fk_local_user_group_assignments_group_id_groups FOREIGN KEY(group_id) REFERENCES `groups` (id), 
    CONSTRAINT fk_local_user_group_assignments_user_id_users FOREIGN KEY(user_id) REFERENCES users (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE network_interfaces (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    name VARCHAR(255) NOT NULL, 
    unique_id VARCHAR(255) NOT NULL, 
    ip_address_id INTEGER UNSIGNED, 
    bond_master TEXT, 
    port_description TEXT, 
    port_number TEXT, 
    port_switch TEXT, 
    port_vlan TEXT, 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_network_interfaces PRIMARY KEY (id), 
    CONSTRAINT fk_network_interfaces_ip_address_id_ip_addresses FOREIGN KEY(ip_address_id) REFERENCES ip_addresses (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE INDEX idx_network_interface_id ON network_interfaces (id);

CREATE UNIQUE INDEX idx_unique_network_interface_unique_id ON network_interfaces (unique_id);

CREATE TABLE physical_racks (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    name VARCHAR(255) NOT NULL, 
    physical_location_id INTEGER UNSIGNED NOT NULL, 
    server_subnet VARCHAR(255), 
    oob_subnet VARCHAR(255), 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_physical_racks PRIMARY KEY (id), 
    CONSTRAINT fk_physical_racks_physical_location_id_physical_locations FOREIGN KEY(physical_location_id) REFERENCES physical_locations (id), 
    CONSTRAINT idx_physical_rack_location UNIQUE (name, physical_location_id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE INDEX idx_physical_rack_id ON physical_racks (id);

CREATE TABLE tag_node_group_assignments (
    tag_id INTEGER UNSIGNED, 
    node_group_id INTEGER UNSIGNED, 
    CONSTRAINT fk_tag_node_group_assignments_node_group_id_node_groups FOREIGN KEY(node_group_id) REFERENCES node_groups (id), 
    CONSTRAINT fk_tag_node_group_assignments_tag_id_tags FOREIGN KEY(tag_id) REFERENCES tags (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE nodes (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    name VARCHAR(255) NOT NULL, 
    unique_id VARCHAR(255) NOT NULL, 
    status_id INTEGER UNSIGNED NOT NULL, 
    hardware_profile_id INTEGER UNSIGNED NOT NULL, 
    operating_system_id INTEGER UNSIGNED NOT NULL, 
    ec2_id INTEGER UNSIGNED, 
    data_center_id INTEGER UNSIGNED, 
    uptime VARCHAR(255), 
    serial_number VARCHAR(255), 
    os_memory VARCHAR(255), 
    processor_count INTEGER, 
    last_registered TIMESTAMP NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_nodes PRIMARY KEY (id), 
    CONSTRAINT fk_nodes_data_center_id_data_centers FOREIGN KEY(data_center_id) REFERENCES data_centers (id), 
    CONSTRAINT fk_nodes_ec2_id_ec2_instances FOREIGN KEY(ec2_id) REFERENCES ec2_instances (id), 
    CONSTRAINT fk_nodes_hardware_profile_id_hardware_profiles FOREIGN KEY(hardware_profile_id) REFERENCES hardware_profiles (id), 
    CONSTRAINT fk_nodes_operating_system_id_operating_systems FOREIGN KEY(operating_system_id) REFERENCES operating_systems (id), 
    CONSTRAINT fk_nodes_status_id_statuses FOREIGN KEY(status_id) REFERENCES statuses (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE UNIQUE INDEX idx_node_ec2_id ON nodes (ec2_id);

CREATE INDEX idx_node_id ON nodes (id);

CREATE INDEX idx_node_name ON nodes (name);

CREATE INDEX idx_node_serial_number ON nodes (serial_number);

CREATE TABLE physical_elevations (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    elevation VARCHAR(11) NOT NULL, 
    physical_rack_id INTEGER UNSIGNED NOT NULL, 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_physical_elevations PRIMARY KEY (id), 
    CONSTRAINT fk_physical_elevations_physical_rack_id_physical_racks FOREIGN KEY(physical_rack_id) REFERENCES physical_racks (id), 
    CONSTRAINT idx_physical_elevation_location UNIQUE (elevation, physical_rack_id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE UNIQUE INDEX idx_physical_elevation_id ON physical_elevations (id);

CREATE TABLE tag_data_center_assignments (
    tag_id INTEGER UNSIGNED, 
    data_center_id INTEGER UNSIGNED, 
    CONSTRAINT fk_tag_data_center_assignments_data_center_id_data_centers FOREIGN KEY(data_center_id) REFERENCES data_centers (id), 
    CONSTRAINT fk_tag_data_center_assignments_tag_id_tags FOREIGN KEY(tag_id) REFERENCES tags (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE hypervisor_vm_assignments (
    hypervisor_id INTEGER UNSIGNED, 
    guest_vm_id INTEGER UNSIGNED, 
    CONSTRAINT fk_hypervisor_vm_assignments_guest_vm_id_nodes FOREIGN KEY(guest_vm_id) REFERENCES nodes (id), 
    CONSTRAINT fk_hypervisor_vm_assignments_hypervisor_id_nodes FOREIGN KEY(hypervisor_id) REFERENCES nodes (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE network_interface_assignments (
    node_id INTEGER UNSIGNED, 
    network_interface_id INTEGER UNSIGNED, 
    CONSTRAINT fk_network_interface_assignments_network_interface_id_ne_7ba3 FOREIGN KEY(network_interface_id) REFERENCES network_interfaces (id), 
    CONSTRAINT fk_network_interface_assignments_node_id_nodes FOREIGN KEY(node_id) REFERENCES nodes (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE node_group_assignments (
    node_id INTEGER UNSIGNED, 
    node_group_id INTEGER UNSIGNED, 
    CONSTRAINT fk_node_group_assignments_node_group_id_node_groups FOREIGN KEY(node_group_id) REFERENCES node_groups (id), 
    CONSTRAINT fk_node_group_assignments_node_id_nodes FOREIGN KEY(node_id) REFERENCES nodes (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE physical_devices (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT, 
    serial_number VARCHAR(255) NOT NULL, 
    physical_location_id INTEGER UNSIGNED NOT NULL, 
    physical_rack_id INTEGER UNSIGNED NOT NULL, 
    physical_elevation_id INTEGER UNSIGNED NOT NULL, 
    status_id INTEGER UNSIGNED NOT NULL, 
    mac_address_1 VARCHAR(255) NOT NULL, 
    mac_address_2 VARCHAR(255), 
    hardware_profile_id INTEGER UNSIGNED NOT NULL, 
    oob_ip_address VARCHAR(255), 
    oob_mac_address VARCHAR(255), 
    created TIMESTAMP NOT NULL, 
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
    updated_by VARCHAR(255) NOT NULL, 
    CONSTRAINT pk_physical_devices PRIMARY KEY (id), 
    CONSTRAINT fk_physical_devices_hardware_profile_id_hardware_profiles FOREIGN KEY(hardware_profile_id) REFERENCES hardware_profiles (id), 
    CONSTRAINT fk_physical_devices_physical_elevation_id_physical_elevations FOREIGN KEY(physical_elevation_id) REFERENCES physical_elevations (id), 
    CONSTRAINT fk_physical_devices_physical_location_id_physical_locations FOREIGN KEY(physical_location_id) REFERENCES physical_locations (id), 
    CONSTRAINT fk_physical_devices_physical_rack_id_physical_racks FOREIGN KEY(physical_rack_id) REFERENCES physical_racks (id), 
    CONSTRAINT fk_physical_devices_status_id_statuses FOREIGN KEY(status_id) REFERENCES statuses (id), 
    CONSTRAINT idx_physical_device_rack_elevation UNIQUE (physical_rack_id, physical_elevation_id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE INDEX idx_physical_device_id ON physical_devices (id);

CREATE UNIQUE INDEX idx_physical_device_serial_number ON physical_devices (serial_number);

CREATE TABLE tag_node_assignments (
    tag_id INTEGER UNSIGNED, 
    node_id INTEGER UNSIGNED, 
    CONSTRAINT fk_tag_node_assignments_node_id_nodes FOREIGN KEY(node_id) REFERENCES nodes (id), 
    CONSTRAINT fk_tag_node_assignments_tag_id_tags FOREIGN KEY(tag_id) REFERENCES tags (id)
)CHARSET=utf8 COLLATE utf8_bin;

CREATE TABLE tag_physical_device_assignments (
    tag_id INTEGER UNSIGNED, 
    physical_device_id INTEGER UNSIGNED, 
    CONSTRAINT fk_tag_physical_device_assignments_physical_device_id_ph_6dc6 FOREIGN KEY(physical_device_id) REFERENCES physical_devices (id), 
    CONSTRAINT fk_tag_physical_device_assignments_tag_id_tags FOREIGN KEY(tag_id) REFERENCES tags (id)
)CHARSET=utf8 COLLATE utf8_bin;

INSERT INTO alembic_version (version_num) VALUES ('b1bf5df56a22');

-- Running upgrade b1bf5df56a22 -> d4574cc94ba8

ALTER TABLE network_interfaces ADD COLUMN mac_address TEXT AFTER bond_master;

ALTER TABLE network_interfaces ADD COLUMN seen_mac_address TEXT AFTER port_vlan;

UPDATE alembic_version SET version_num='d4574cc94ba8' WHERE alembic_version.version_num = 'b1bf5df56a22';

-- Running upgrade d4574cc94ba8 -> 3ee80746cca8

ALTER TABLE physical_locations ADD COLUMN status_id INTEGER UNSIGNED NOT NULL AFTER phone_number;

ALTER TABLE physical_locations ADD CONSTRAINT fk_physical_locations_status_id_statuses FOREIGN KEY(status_id) REFERENCES statuses (id);

UPDATE alembic_version SET version_num='3ee80746cca8' WHERE alembic_version.version_num = 'd4574cc94ba8';

