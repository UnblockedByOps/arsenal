'''Data for testing node registration scenarios.'''

REGISTER_TEST_CASES = {
    'single_interface': {
        'ec2': None,
        'guest_vms': [],
        'hardware_profile': {
            'manufacturer': 'VMware, Inc.',
            'model': 'VMware Virtual Platform',
            'name': 'VMware, Inc. VMware Virtual Platform'
        },
        'name': 'server0000.internal',
        'network_interfaces': [
            {
                'ip_address': '10.1.1.20',
                'name': 'eth0',
                'unique_id': '00:50:56:bf:4b:f3'
            }
        ],
        'operating_system': {
            'architecture': 'x86_64',
            'description': 'CentOS Linux release 7.3.1611 (Core)',
            'name': 'CentOS 7.3.1611 x86_64',
            'variant': 'CentOS',
            'version_number': '7.3.1611'
        },
        'processor_count': 2,
        'serial_number': '987654321-0',
        'unique_id': '123456789-0',
        'uptime': '1 day'
    },
    'multi_interface_bonded': {
        'ec2': None,
        'guest_vms': [],
        'hardware_profile': {
            'manufacturer': 'HP',
            'model': 'ProLiant DL360 Gen9',
            'name': 'HP ProLiant DL360 Gen9'
        },
        'name': 'server0001.internal',
        'network_interfaces': [
            {
                'ip_address': '10.1.1.21',
                'name': 'bond0',
                'unique_id': 'bond0_123456789-1'
            },
            {
                'bond_master': 'bond0',
                'ip_address': '10.1.1.21',
                'name': 'eth1',
                'port_description': 'UNKNOWN',
                'port_number': 'Ethernet23',
                'port_switch': 'switch-2.dc1',
                'port_vlan': '960',
                'unique_id': '5c:b9:01:90:5d:dd'
            },
            {
                'bond_master': 'bond0',
                'ip_address': '10.1.1.21',
                'name': 'eth0',
                'port_description': 'UNKNOWN',
                'port_number': 'Ethernet23',
                'port_switch': 'switch-1.dc1',
                'port_vlan': '960',
                'unique_id': '5c:b9:01:90:5d:dc'
            }
        ],
        'operating_system': {
            'architecture': 'x86_64',
            'description': 'CentOS Linux release 7.3.1611 (Core)',
            'name': 'CentOS 7.3.1611 x86_64',
            'variant': 'CentOS',
            'version_number': '7.3.1611'
        },
        'processor_count': 40,
        'serial_number': '987654321-1',
        'unique_id': '123456789-1',
        'uptime': '1 day'
    },
    'multi_interface_no_bond': {
        'ec2': None,
        'guest_vms': [],
        'hardware_profile': {
            'manufacturer': 'HP',
            'model': 'ProLiant DL360p Gen8',
            'name': 'HP ProLiant DL360p Gen8'
        },
        'name': 'server0002.internal',
        'network_interfaces': [
            {
                'name': 'eth1',
                'unique_id': '48:df:37:17:6e:c0'
            },
            {
                'bond_master': '',
                'ip_address': '10.1.1.22',
                'name': 'eth0',
                'port_description': 'eth0.server0002.internal',
                'port_number': 'Ethernet22',
                'port_switch': 'switch-2.dc1',
                'port_vlan': '2000',
                'unique_id': '48:df:37:17:6e:c1'
            }
        ],
        'operating_system': {
            'architecture': 'x86_64',
            'description': 'CentOS Linux release 7.4.1708 (Core)',
            'name': 'CentOS 7.4.1708 x86_64',
            'variant': 'CentOS',
            'version_number': '7.4.1708'
        },
        'processor_count': 32,
        'serial_number': '987654321-2',
        'unique_id': '123456789-2',
        'uptime': '1 day'
    },
    'single_interface_ec2': {
        'ec2': {
            'ec2_ami_id': 'ami-e3415983',
            'ec2_hostname': 'ip-10-60-3-114.usw1.fanops.net',
            'ec2_instance_id': 'i-129485tu8549',
            'ec2_instance_type': 'm5.xlarge',
            'ec2_availability_zone': 'us-east-1',
            'ec2_profile': 'hvm',
            'ec2_reservation_id': '12345',
            'ec2_security_groups': 'default',
        },
        'guest_vms': [],
        'hardware_profile': {
            'manufacturer': 'Amazon EC2',
            'model': 'm5.xlarge',
            'name': 'Amazon EC2 m5.xlarge'
        },
        'name': 'server0003.internal',
        'network_interfaces': [
            {
                'ip_address': '10.1.1.23',
                'name': 'eth0',
                'unique_id': '00:50:56:bf:4b:aa'
            }
        ],
        'operating_system': {
            'architecture': 'x86_64',
            'description': 'CentOS Linux release 7.4.1708 (Core)',
            'name': 'CentOS 7.4.1708 x86_64',
            'variant': 'CentOS',
            'version_number': '7.4.1708'
        },
        'processor_count': 2,
        'serial_number': '987654321-1',
        'unique_id': 'i-0c1abf92f3b6c33b1',
        'uptime': '1 day'
    }
}
