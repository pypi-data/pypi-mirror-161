import random
import time
from robertcommondriver.system.iot.iot_plc_s7 import IOTPlcS7


def logging_print(**kwargs):
    print(kwargs)


def test_simulate():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'send_timeout': 15, 'rec_timeout': 3500}
    dict_point = {}
    dict_point['plc111'] = {'point_writable': True, 'point_name': 'plc111', 'point_device_address': 102, 'point_address': 'DB3,REAL4', 'point_scale': '1'}
    dict_point['plc211'] = {'point_writable': True, 'point_name': 'plc211', 'point_device_address': 102, 'point_address': 'DB3,REAL8', 'point_scale': '1'}
    dict_point['plc1'] = {'point_writable': True, 'point_name': 'plc1', 'point_device_address': 102, 'point_address': 'DB15,INT0', 'point_scale': '1'}
    dict_point['plc2'] = {'point_writable': True, 'point_name': 'plc2', 'point_device_address': 102, 'point_address': 'DB15,INT1', 'point_scale': '1'}
    dict_point['plc3'] = {'point_writable': True, 'point_name': 'plc3', 'point_device_address': 102, 'point_address': 'DB3,BOOL4.0', 'point_scale': '1'}
    dict_point['plc4'] = {'point_writable': True, 'point_name': 'plc4', 'point_device_address': 102, 'point_address': 'DB15,WORD5', 'point_scale': '1'}
    dict_point['plc5'] = {'point_writable': True, 'point_name': 'plc5', 'point_device_address': 102, 'point_address': 'DB15,DWORD22', 'point_scale': '1'}
    dict_point['plc6'] = {'point_writable': True, 'point_name': 'plc6', 'point_device_address': 102, 'point_address': 'DB3,INT28', 'point_scale': '1'}
    dict_point['plc7'] = {'point_writable': True, 'point_name': 'plc7', 'point_device_address': 102, 'point_address': 'DB15,REAL38', 'point_scale': '1'}
    dict_point['plc8'] = {'point_writable': True, 'point_name': 'plc8', 'point_device_address': 102, 'point_address': 'DB15,INT42', 'point_scale': '1'}
    dict_point['plc9'] = {'point_writable': True, 'point_name': 'plc9', 'point_device_address': 102, 'point_address': 'DB3,WORD44', 'point_scale': '1'}
    dict_point['plc10'] = {'point_writable': True, 'point_name': 'plc10', 'point_device_address': 102, 'point_address': 'I0.0', 'point_scale': '1'}
    dict_point['plc11'] = {'point_writable': True, 'point_name': 'plc11', 'point_device_address': 102, 'point_address': 'Q0.0', 'point_scale': '1'}
    dict_point['plc12'] = {'point_writable': True, 'point_name': 'plc12', 'point_device_address': 102, 'point_address': 'MW300', 'point_scale': '1'}
    dict_point['plc13'] = {'point_writable': True, 'point_name': 'plc13', 'point_device_address': 102, 'point_address': 'M5.7', 'point_scale': '1'}

    client = IOTPlcS7(configs = dict_config, points= dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            for name, point in dict_point.items():
                point['point_value'] = f"{random.randint(1, 100)}"
            client.simulate(points=dict_point)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


def test_read():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'send_timeout': 15, 'rec_timeout': 3500}
    dict_point = {}
    dict_point['plc1'] = {'point_writable': True, 'point_name': 'plc1', 'point_device_address': '192.168.1.100/102/0/1', 'point_address': 'DB15,INT0', 'point_scale': '1'}
    dict_point['plc2'] = {'point_writable': True, 'point_name': 'plc2', 'point_device_address': '192.168.1.100/102/0/1', 'point_address': 'DB15,INT1', 'point_scale': '1'}
    dict_point['plc3'] = {'point_writable': True, 'point_name': 'plc3', 'point_device_address': '192.168.1.100/102/0/1', 'point_address': 'DB3,BOOL4.0', 'point_scale': '1'}
    dict_point['plc4'] = {'point_writable': True, 'point_name': 'plc4', 'point_device_address': '192.168.1.100/102/0/1', 'point_address': 'DB15,WORD5', 'point_scale': '1'}
    dict_point['plc5'] = {'point_writable': True, 'point_name': 'plc5', 'point_device_address': '192.168.1.100/102/0/1', 'point_address': 'DB15,DWORD22', 'point_scale': '1'}
    dict_point['plc6'] = {'point_writable': True, 'point_name': 'plc6', 'point_device_address': '192.168.1.100/102/0/1', 'point_address': 'DB3,INT28', 'point_scale': '1'}
    dict_point['plc7'] = {'point_writable': True, 'point_name': 'plc7', 'point_device_address': '192.168.1.100/102/0/1', 'point_address': 'DB15,REAL38', 'point_scale': '1'}
    dict_point['plc8'] = {'point_writable': True, 'point_name': 'plc8', 'point_device_address': '192.168.1.100/102/0/1', 'point_address': 'DB15,INT42', 'point_scale': '1'}
    dict_point['plc9'] = {'point_writable': True, 'point_name': 'plc9', 'point_device_address': '192.168.1.100/102/0/1', 'point_address': 'DB3,WORD44', 'point_scale': '1'}
    dict_point['plc10'] = {'point_writable': True, 'point_name': 'plc10', 'point_device_address': '192.168.1.100/102/0/1', 'point_address': 'I0.0', 'point_scale': '1'}
    dict_point['plc11'] = {'point_writable': True, 'point_name': 'plc11', 'point_device_address': '192.168.1.100/102/0/1', 'point_address': 'Q0.0', 'point_scale': '1'}
    dict_point['plc12'] = {'point_writable': True, 'point_name': 'plc12', 'point_device_address': '192.168.1.100/102/0/1', 'point_address': 'MW300', 'point_scale': '1'}
    dict_point['plc13'] = {'point_writable': True, 'point_name': 'plc13', 'point_device_address': '192.168.1.100/102/0/1', 'point_address': 'M5.7', 'point_scale': '1'}
    client = IOTPlcS7(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            re = client.read()
            print(re)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


test_simulate()