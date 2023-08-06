import random
import time
from robertcommondriver.system.iot.iot_modbus import IOTModbus


def logging_print(**kwargs):
    print(kwargs)


def test_read():
    #配置项
    dict_config = {
                        'multi_read': 100,                             # 批量读取个数
                        'cmd_interval': 0.3,                         # 命令间隔
                        'time_out': 5                                 # 超时时间
                    }
    #点表
    dict_point = {}
    dict_point['modbus_0'] = {'point_writable': True, 'point_name': 'modbus_0', 'point_device_address': '192.168.1.184/502',  'point_slave_id': 1, 'point_fun_code': 3, 'point_address': 0, 'point_data_type': 5, 'point_data_length': 2, 'point_scale':'1'}
    dict_point['modbus_1'] = {'point_writable': True, 'point_name': 'modbus_1', 'point_device_address': '192.168.1.184/502', 'point_slave_id': 1,'point_fun_code': 3, 'point_address': 2, 'point_data_type': 5, 'point_data_length': 2, 'point_scale': '1'}
    dict_point['modbus_2'] = {'point_writable': True, 'point_name': 'modbus_2', 'point_device_address': '192.168.1.184/502', 'point_slave_id': 1,'point_fun_code': 3, 'point_address': 4, 'point_data_type': 5, 'point_data_length': 2, 'point_scale': '1'}

    dict_point['signed'] = {'point_writable': True, 'point_name': 'signed', 'point_device_address': '192.168.1.172/502',  'point_slave_id': 2, 'point_fun_code': 3, 'point_address': 0, 'point_data_type': 0, 'point_data_length': 1, 'point_scale':'1'}
    dict_point['unsigned'] = {'point_writable': True, 'point_name': 'unsigned', 'point_device_address': '192.168.1.172/502', 'point_slave_id': 2,'point_fun_code': 3, 'point_address': 1, 'point_data_type': 1, 'point_data_length': 1, 'point_scale': '1'}
    dict_point['bit'] = {'point_writable': True, 'point_name': 'bit', 'point_device_address': '192.168.1.172/502', 'point_slave_id': 2,'point_fun_code': 3, 'point_address': 2, 'point_data_type': 2, 'point_data_length': 1, 'point_scale': '1'}
    dict_point['long'] = {'point_writable': True, 'point_name': 'long', 'point_device_address': '192.168.1.172/502',  'point_slave_id': 2, 'point_fun_code': 3, 'point_address': 4, 'point_data_type': 3, 'point_data_length': 2, 'point_scale':'1'}
    dict_point['long_rev'] = {'point_writable': True, 'point_name': 'long_rev', 'point_device_address': '192.168.1.172/502', 'point_slave_id': 2,'point_fun_code': 3, 'point_address': 6, 'point_data_type': 4, 'point_data_length': 2, 'point_scale': '1'}
    dict_point['float'] = {'point_writable': True, 'point_name': 'float', 'point_device_address': '192.168.1.172/502', 'point_slave_id': 2,'point_fun_code': 3, 'point_address': 10, 'point_data_type': 5, 'point_data_length': 2, 'point_scale': '1'}
    dict_point['float_rev'] = {'point_writable': True, 'point_name': 'float_rev', 'point_device_address': '192.168.1.172/502',  'point_slave_id': 2, 'point_fun_code': 3, 'point_address': 12, 'point_data_type': 6, 'point_data_length': 2, 'point_scale':'1'}
    dict_point['double'] = {'point_writable': True, 'point_name': 'double', 'point_device_address': '192.168.1.172/502', 'point_slave_id': 2,'point_fun_code': 3, 'point_address': 16, 'point_data_type': 7, 'point_data_length': 4, 'point_scale': '1'}
    dict_point['double_rev'] = {'point_writable': True, 'point_name': 'double_rev', 'point_device_address': '192.168.1.172/502', 'point_slave_id': 2,'point_fun_code': 3, 'point_address': 24, 'point_data_type': 8, 'point_data_length': 4, 'point_scale': '1'}

    modbus_driver = IOTModbus(configs=dict_config, points=dict_point)
    modbus_driver.logging(call_logging=logging_print)
    # 轮询全部
    while True:
        dict_result_scrap = modbus_driver.read()
        time.sleep(2)


def test_write():
    # 配置项
    dict_config = {
        'multi_read': 100,  # 批量读取个数
        'cmd_interval': 0.3,  # 命令间隔
        'time_out': 5  # 超时时间
    }
    # 点表
    dict_point = {}
    dict_point['signed'] = {'point_writable': True, 'point_name': 'signed', 'point_device_address': '192.168.1.172/502',
                            'point_slave_id': 2, 'point_fun_code': 3, 'point_address': 0, 'point_data_type': 0,
                            'point_data_length': 1, 'point_scale': '1'}
    dict_point['unsigned'] = {'point_writable': True, 'point_name': 'unsigned',
                              'point_device_address': '192.168.1.172/502', 'point_slave_id': 2, 'point_fun_code': 3,
                              'point_address': 1, 'point_data_type': 1, 'point_data_length': 1, 'point_scale': '1'}
    dict_point['bit'] = {'point_writable': True, 'point_name': 'bit', 'point_device_address': '192.168.1.172/502',
                         'point_slave_id': 2, 'point_fun_code': 3, 'point_address': 2, 'point_data_type': 2,
                         'point_data_length': 1, 'point_scale': '1'}
    dict_point['long'] = {'point_writable': True, 'point_name': 'long', 'point_device_address': '192.168.1.172/502',
                          'point_slave_id': 2, 'point_fun_code': 3, 'point_address': 4, 'point_data_type': 3,
                          'point_data_length': 2, 'point_scale': '1'}
    dict_point['long_rev'] = {'point_writable': True, 'point_name': 'long_rev',
                              'point_device_address': '192.168.1.172/502', 'point_slave_id': 2, 'point_fun_code': 3,
                              'point_address': 6, 'point_data_type': 4, 'point_data_length': 2, 'point_scale': '1'}
    dict_point['float'] = {'point_writable': True, 'point_name': 'float', 'point_device_address': '192.168.1.172/502',
                           'point_slave_id': 2, 'point_fun_code': 3, 'point_address': 10, 'point_data_type': 5,
                           'point_data_length': 2, 'point_scale': '1'}
    dict_point['float_rev'] = {'point_writable': True, 'point_name': 'float_rev',
                               'point_device_address': '192.168.1.172/502', 'point_slave_id': 2, 'point_fun_code': 3,
                               'point_address': 12, 'point_data_type': 6, 'point_data_length': 2, 'point_scale': '1'}
    dict_point['double'] = {'point_writable': True, 'point_name': 'double', 'point_device_address': '192.168.1.172/502',
                            'point_slave_id': 2, 'point_fun_code': 3, 'point_address': 16, 'point_data_type': 7,
                            'point_data_length': 4, 'point_scale': '1'}
    dict_point['double_rev'] = {'point_writable': True, 'point_name': 'double_rev',
                                'point_device_address': '192.168.1.172/502', 'point_slave_id': 2, 'point_fun_code': 3,
                                'point_address': 24, 'point_data_type': 8, 'point_data_length': 4, 'point_scale': '1'}

    modbus_driver = IOTModbus(configs=dict_config, points=dict_point)
    modbus_driver.logging(call_logging=logging_print)
    # 轮询全部
    while True:
        dict_result_scrap = modbus_driver.write(values={'double_rev': -123.45})
        time.sleep(2)


def test_smiluate():
    #配置项
    dict_config = {
                        'cmd_interval': 0.3,                         # 命令间隔
                        'time_out': 5                                 # 超时时间
                    }
    #点表
    dict_point = {}
    dict_point['signed'] = {'point_writable': True, 'point_name': 'signed', 'point_device_address': '0.0.0.0/502',  'point_slave_id': 2, 'point_fun_code': 3, 'point_address': 0, 'point_data_type': 6, 'point_data_length': 1, 'point_data_order': 0, 'point_scale':'1', 'point_value': -12}
    dict_point['unsigned'] = {'point_writable': True, 'point_name': 'unsigned', 'point_device_address': '0.0.0.0/502', 'point_slave_id': 2,'point_fun_code': 3, 'point_address': 1, 'point_data_type': 8, 'point_data_length': 1, 'point_data_order': 0, 'point_scale': '1', 'point_value': 211}
    dict_point['bit'] = {'point_writable': True, 'point_name': 'bit', 'point_device_address': '0.0.0.0/502', 'point_slave_id': 2,'point_fun_code': 3, 'point_address': 2, 'point_data_type': 1, 'point_data_length': 1, 'point_data_order': 0, 'point_scale': '1', 'point_value': 1}
    dict_point['bit1'] = {'point_writable': True, 'point_name': 'bit1', 'point_device_address': '0.0.0.0/502', 'point_slave_id': 2,'point_fun_code': 3, 'point_address': 2, 'point_data_type': 1, 'point_data_length': 3, 'point_data_order': 0, 'point_scale': '1', 'point_value': 1}
    dict_point['long'] = {'point_writable': True, 'point_name': 'long', 'point_device_address': '0.0.0.0/502',  'point_slave_id': 2, 'point_fun_code': 3, 'point_address': 4, 'point_data_type': 12, 'point_data_length': 2, 'point_data_order': 0, 'point_scale':'1', 'point_value': 123}
    dict_point['long_rev'] = {'point_writable': True, 'point_name': 'long_rev', 'point_device_address': '0.0.0.0/502', 'point_slave_id': 2,'point_fun_code': 3, 'point_address': 6, 'point_data_type': 12, 'point_data_length': 2, 'point_data_order': 2, 'point_scale': '1', 'point_value': 134}
    dict_point['float'] = {'point_writable': True, 'point_name': 'float', 'point_device_address': '0.0.0.0/502', 'point_slave_id': 2,'point_fun_code': 3, 'point_address': 10, 'point_data_type': 18, 'point_data_length': 2, 'point_data_order': 0, 'point_scale': '1', 'point_value': -1.23}
    dict_point['float_rev'] = {'point_writable': True, 'point_name': 'float_rev', 'point_device_address': '0.0.0.0/502',  'point_slave_id': 2, 'point_fun_code': 3, 'point_address': 12, 'point_data_type': 18, 'point_data_length': 2, 'point_data_order': 2, 'point_scale':'1', 'point_value': 1.23}
    dict_point['double'] = {'point_writable': True, 'point_name': 'double', 'point_device_address': '0.0.0.0/502', 'point_slave_id': 2,'point_fun_code': 3, 'point_address': 16, 'point_data_type': 20, 'point_data_length': 4, 'point_data_order': 0, 'point_scale': '1', 'point_value': 1.2345}
    dict_point['double_rev'] = {'point_writable': True, 'point_name': 'double_rev', 'point_device_address': '0.0.0.0/502', 'point_slave_id': 2,'point_fun_code': 3, 'point_address': 24, 'point_data_type': 20, 'point_data_length': 4, 'point_data_order': 2, 'point_scale': '1', 'point_value': -1.2345}

    client = IOTModbus(configs=dict_config, points={})
    client.logging(call_logging=logging_print)
    # 轮询全部
    while True:
        #for name, point in dict_point.items():
        #    point['point_value'] = random.randint(1, 100)
        client.simulate(points=dict_point)
        time.sleep(10)


test_smiluate()

