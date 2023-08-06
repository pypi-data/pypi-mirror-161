import random
import time
from robertcommondriver.system.iot.iot_bacnet import IOTBacnet, Address


def logging_print(**kwargs):
    print(kwargs)


def callback_set_value(**kwargs):
    print(kwargs)


def test_driver():

    dict_config = {
        'address': '192.168.1.36/24:47809',  # bacnet server ip(绑定网卡)
        'identifier': 555,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 'segmentedBoth',  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'multi_read': 20,  # bacnet 批量读取个数
        'cmd_interval': 0.3,  # bacnet命令间隔
        'time_out': 5000  # 超时时间
    }

    dict_point = {'6_4_1_analogValue_1': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True',
                                          'point_device_address': '6:4/604/192.168.1.184', 'point_type': 'analogValue',
                                          'point_property': 'presentValue', 'point_address': 1,
                                          'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
                  '6_4_2_analogValue_2': {'point_name': '6_4_2_analogValue_2', 'index': 3, 'point_writable': 'True',
                                          'point_device_address': '192.168.1.172', 'point_type': 'analogInput',
                                          'point_property': 'presentValue', 'point_address': 3,
                                          'point_description': '', 'objectName': 'Random-604-2', 'presentValue': '2.0'},
                  }

    points = {'6_4_1_analogValue_1': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.171', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 0, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_12': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 1, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_13': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 2, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_14': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 3, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_15': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 4, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_16': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 5, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_17': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 6, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_18': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 7, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_19': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 8, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_110': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 9, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_111': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 10, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_112': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 11, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_113': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 12, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_114': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 13, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_115': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 14, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_116': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 15, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_117': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 16, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_118': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 17, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_119': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 18, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_120': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': 19, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_121': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogOutput', 'point_property': 'presentValue', 'point_address': 0, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_122': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogOutput', 'point_property': 'presentValue', 'point_address': 1, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_123': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogOutput', 'point_property': 'presentValue', 'point_address': 2, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_124': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogOutput', 'point_property': 'presentValue', 'point_address': 4, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_125': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogOutput', 'point_property': 'presentValue', 'point_address': 6, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_126': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'analogOutput', 'point_property': 'presentValue', 'point_address': 17, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_127': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'binaryInput', 'point_property': 'presentValue', 'point_address': 1, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_128': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'binaryInput', 'point_property': 'presentValue', 'point_address': 2, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_129': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'binaryInput', 'point_property': 'presentValue', 'point_address': 3, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_130': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'binaryInput', 'point_property': 'presentValue', 'point_address': 4, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_131': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'binaryInput', 'point_property': 'presentValue', 'point_address': 5, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_132': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'binaryInput', 'point_property': 'presentValue', 'point_address': 7, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_133': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'binaryOutput', 'point_property': 'presentValue', 'point_address': 1, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_134': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'binaryOutput', 'point_property': 'presentValue', 'point_address': 3, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_135': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'binaryOutput', 'point_property': 'presentValue', 'point_address': 4, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_136': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'binaryOutput', 'point_property': 'presentValue', 'point_address': 5, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_137': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'binaryOutput', 'point_property': 'presentValue', 'point_address': 7, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_138': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'binaryOutput', 'point_property': 'presentValue', 'point_address': 11, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_139': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'binaryOutput', 'point_property': 'presentValue', 'point_address': 13, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_140': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'binaryOutput', 'point_property': 'presentValue', 'point_address': 14, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_141': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'multiStateInput', 'point_property': 'presentValue', 'point_address': 0, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_142': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '192.168.1.172', 'point_type': 'multiStateOutput', 'point_property': 'presentValue', 'point_address': 0, 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
              }

    client = IOTBacnet(configs = dict_config, points= points)
    client.logging(call_logging=logging_print)
    while True:
        try:
            # results = client.discover(retries=2)

            #results = client.scan(address='6:4/604/192.168.1.184')
            # results = client.scan()


            # print(client.ping(address='6:4/604/192.168.1.184'))

            print(client.write(values={'6_4_1_analogValue_14': 21, '6_4_1_analogValue_15': 22}))

            results = client.read()
            print(results)


        except Exception as e:
            print(e.__str__())
        time.sleep(4)


def test_simulate():

    dict_config = {
        'address': '192.168.1.36/24:47808',  # bacnet server ip(绑定网卡)
        'identifier': 555,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 'segmentedBoth',  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'time_out': 10000  # 超时时间
    }

    dict_point = {'6_4_1_analogValue_1': {'point_writable': 'True', 'point_name': '6_4_1_analogValue_1', 'point_type': 'analogValue', 'point_address': 1, 'point_value': 1.0, 'point_description': '6_4_1 analogValue 1'},
                  '6_4_2_analogValue_2': {'point_writable': 'True', 'point_name': '6_4_2_analogValue_2', 'point_type': 'analogValue', 'point_address': 2, 'point_value': 2.0, 'point_description': '6_4_2 analogValue 2'},
                  }

    client = IOTBacnet(configs = dict_config, points= dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            #for name, point in dict_point.items():
            #    point['point_value'] = f"{random.randint(1, 100)}"
            client.simulate(points=dict_point, callbacks={'set_value': callback_set_value})
        except Exception as e:
            print(e.__str__())
        time.sleep(120)


def test_address():

    aa = Address('26002:0x000000018864')

    dict_config = {
        'address': '192.168.1.136/24:47809',  # bacnet server ip(绑定网卡)
        'identifier': 555,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 'segmentedBoth',  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'multi_read': 20,  # bacnet 批量读取个数
        'cmd_interval': 0.3,  # bacnet命令间隔
        'time_out': 5000  # 超时时间
    }

    dict_point = {'6_4_1_analogValue_1': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True',
                                          'point_device_address': '6:4/604/192.168.1.184', 'point_type': 'analogValue',
                                          'point_property': 'presentValue', 'point_address': 1,
                                          'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
                  '6_4_2_analogValue_2': {'point_name': '6_4_2_analogValue_2', 'index': 3, 'point_writable': 'True',
                                          'point_device_address': '192.168.1.172', 'point_type': 'analogInput',
                                          'point_property': 'presentValue', 'point_address': 3,
                                          'point_description': '', 'objectName': 'Random-604-2', 'presentValue': '2.0'},
                  }

    client = IOTBacnet(configs=dict_config, points=dict_point)
    while True:
        try:

            results = client.read(ping_check=False)
            print(results)


        except Exception as e:
            print(e.__str__())
        time.sleep(4)


def test_scan():

    dict_config = {
        'address': '192.168.1.36/24:47808',  # bacnet server ip(绑定网卡)
        'identifier': 555,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 'segmentedBoth',  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'multi_read': 20,  # bacnet 批量读取个数
        'cmd_interval': 0.3,  # bacnet命令间隔
        'time_out': 5000  # 超时时间
    }

    client = IOTBacnet(configs = dict_config, points={})
    client.logging(call_logging=logging_print)
    while True:
        try:
            # print(client.discover())

            # results = client.ping(address='192.168.1.255')

            results = client.ping(address='6:4/604/192.168.1.184')
            print(results)

            results = client.ping(address='6:4/604/192.168.1.184')
            print(results)
            # results = client.ping(address='192.168.1.184')

            # results = client.scan(address='6:4/604/192.168.1.184')
            results = client.scan(address='6:4/604/192.168.1.184', ping_check=False)
            # print(client.scan())
            print(results)
        except Exception as e:
            print(e.__str__())
        time.sleep(4)


def test_whois():
    dict_config = {
        'address': '192.168.1.36/24:47808',  # bacnet server ip(绑定网卡)
        'identifier': 555,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 'segmentedBoth',  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'multi_read': 20,  # bacnet 批量读取个数
        'cmd_interval': 0.3,  # bacnet命令间隔
        'time_out': 5000  # 超时时间
    }

    client = IOTBacnet(configs=dict_config, points={})
    client.logging(call_logging=logging_print)
    count = 0
    results = client.discover()
    while count != len(results):
        sleep = 5
        while sleep > 0:
            sleep = sleep - 1
            time.sleep(1)
        count = len(results)
        results = client.discover()

    print('finish')


test_simulate()