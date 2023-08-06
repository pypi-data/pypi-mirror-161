from robertcommondriver.system.iot.iot_snmp import IOTSNMP


def logging_print(**kwargs):
    print(kwargs)


def test_discover():
    dict_config = {
        "cmd_timeout": 3,
        "cmd_retries": 3,
        "cmd_interval": 0.3,
        "multi_read": 20
       }

    client = IOTSNMP(configs=dict_config, points={})
    client.logging(call_logging=logging_print)
    result = client.discover(address='192.168.1.36/24')
    print(result)


def test_ping():
    dict_config = {
        "cmd_timeout": 3,
        "cmd_retries": 3,
        "cmd_interval": 0.3,
        "multi_read": 20
    }

    client = IOTSNMP(configs=dict_config, points={})
    client.logging(call_logging=logging_print)
    result = client.ping(host='192.168.1.255')
    print(result)


def test_scan():
    dict_config = {
        "cmd_timeout": 3,
        "cmd_retries": 3,
        "cmd_interval": 0.3,
        "multi_read": 20
    }

    client = IOTSNMP(configs=dict_config, points={})
    client.logging(call_logging=logging_print)
    result = client.scan(address='192.168.1.200/161/v1/public/private')
    print(result)


def test_read():
    dict_config = {
        "cmd_timeout": 3,
        "cmd_retries": 3,
        "cmd_interval": 0.3,
        "multi_read": 20
    }

    dict_point = {}
    dict_point['snmp1'] = {'point_writable': True, 'point_name': 'snmp1', 'point_device_address': '192.168.1.200/161/v1/public/private', 'point_oid': '1.3.6.1.2.1.1.1.0', 'point_scale': '1'}
    dict_point['snmp2'] = {'point_writable': True, 'point_name': 'snmp2', 'point_device_address': '192.168.1.200/161/v1/public/private', 'point_oid': '1.3.6.1.2.1.1.2.0', 'point_scale': '1'}
    dict_point['snmp3'] = {'point_writable': True, 'point_name': 'snmp3', 'point_device_address': '192.168.1.200/161/v1/public/private', 'point_oid': '1.3.6.1.2.1.1.3.0', 'point_scale': '1'}
    dict_point['snmp4'] = {'point_writable': True, 'point_name': 'snmp4', 'point_device_address': '192.168.1.200/161/v1/public/private', 'point_oid': '1.3.6.1.2.1.1.4.0', 'point_scale': '1'}

    client = IOTSNMP(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    result = client.read()
    print(result)


test_scan()

