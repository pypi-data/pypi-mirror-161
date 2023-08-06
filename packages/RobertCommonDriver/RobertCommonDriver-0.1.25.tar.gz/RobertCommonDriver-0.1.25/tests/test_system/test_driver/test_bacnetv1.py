import random
import time
from robertcommondriver.system.driver.bacnet_v1 import BacnetClient, SimulateObject, BacnetDriver


def test_read():
    dict_config = {
        'address': '192.168.1.36/24:47808',  # bacnet server ip(绑定网卡)
        'identifier': 555,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 'segmentedBoth',  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'multi_read': 20,  # bacnet 批量读取个数
        'cmd_interval': 0.3,  # bacnet命令间隔
        'time_out': 3000  # 超时时间
    }

    client = BacnetClient(**dict_config)
    result = client.read_property('6:2', 'analogValue', 1, 'presentValue')
    print(result)

def test_cov():

    dict_config = {
        'address': '192.168.1.36/24:47808',  # bacnet server ip(绑定网卡)
        'identifier': 555,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 'segmentedBoth',  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'multi_read': 20,  # bacnet 批量读取个数
        'cmd_interval': 0.3,  # bacnet命令间隔
        'time_out': 3000  # 超时时间
    }

    client = BacnetClient(**dict_config)
    result = client.cov('6:2', 'analogValue', 1, 180, True)
    print(result)


def test_scan():
    dict_config = {
        'address': '192.168.1.36/24:47809',  # bacnet server ip(绑定网卡)
        'identifier': 555,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 'segmentedBoth',  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'multi_read': 20,  # bacnet 批量读取个数
        'cmd_interval': 0.3,  # bacnet命令间隔
        'time_out': 3000  # 超时时间
    }

    client = BacnetClient(**dict_config)
    objects = client.scan('6:2', '192.168.1.184', True)
    print(client.devices())
    reads = []
    for object in objects:
        target_address, object_type, instance_number = object.split('_')
        reads.append([object_type, int(instance_number), 'presentValue'])
    values = client.read('6:2', reads, '192.168.1.184')
    print(values)
    print(client.devices())


def test_simulate():
    dict_config = {
        'address': '192.168.1.36/24:47808',  # bacnet server ip(绑定网卡)
        'identifier': 555,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 'segmentedBoth',  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'multi_read': 20,  # bacnet 批量读取个数
        'cmd_interval': 0.3,  # bacnet命令间隔
        'time_out': 3000  # 超时时间
    }

    client = BacnetClient(**dict_config)
    objects = [SimulateObject('analogInput', 0, 0), SimulateObject('analogOutput', 0, 0), SimulateObject('analogValue', 0, 0), SimulateObject('binaryInput', 0, 0)]
    client.simluate(objects)
    while True:
        client.update_object('analogInput', 0, random.randint(0,100))
        client.update_object('analogOutput', 0, random.randint(0, 100))
        client.update_object('analogValue', 0, random.randint(0, 100))
        client.update_object('binaryInput', 0, random.randint(0, 100))
        time.sleep(1)


def test_driver():
    dict_config = {
        'address': '192.168.1.36/24:47808',  # bacnet server ip(绑定网卡)
        'identifier': 555,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 'segmentedBoth',  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'multi_read': 20,  # bacnet 批量读取个数
        'cmd_interval': 0.3,  # bacnet命令间隔
        'time_out': 3000  # 超时时间
    }

    dict_point = {'6_4_1_analogValue_1': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True',
                                          'point_device_address': '6:4', 'point_type': 'analogValue',
                                          'point_property': 'presentValue', 'point_address': 1,
                                          'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
                  '6_4_2_analogValue_2': {'point_name': '6_4_2_analogValue_2', 'index': 3, 'point_writable': 'True',
                                          'point_device_address': '192.168.1.208', 'point_type': 'analogInput',
                                          'point_property': 'presentValue', 'point_address': 3,
                                          'point_description': '', 'objectName': 'Random-604-2', 'presentValue': '2.0'},
                  # '6_4_3_analogValue_3': {'point_name': '6_4_3_analogValue_3', 'index': 4, 'point_writable': 'True', 'point_device_address': '6:4/604','point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '3', 'point_description': '', 'objectName': 'Random-604-3', 'presentValue': '3.0'},
                  # '6_4_4_analogValue_4': {'point_name': '6_4_4_analogValue_4', 'index': 5, 'point_writable': 'True', 'point_device_address': '6:4/604', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '4', 'point_description': '', 'objectName': 'Random-604-4', 'presentValue': '4.0'},
                  # '6_4_5_analogValue_5':  {'point_name': '6_4_5_analogValue_5', 'index': 6, 'point_writable': 'True', 'point_device_address': '6:4/604', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '5', 'point_description': '', 'objectName': 'Random-604-5', 'presentValue': '5.0'},
                  # '6_4_6_analogValue_6': {'point_name': '6_4_6_analogValue_6', 'index': 7, 'point_writable': 'True', 'point_device_address': '6:4/604', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '6', 'point_description': '', 'objectName': 'Random-604-6', 'presentValue': '6.0'},
                  # '6_4_7_analogValue_7': {'point_name': '6_4_7_analogValue_7', 'index': 8, 'point_writable': 'True', 'point_device_address': '6:4/604', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '7', 'point_description': '', 'objectName': 'Random-604-7', 'presentValue': '7.0'},
                  # '6_4_8_analogValue_8': {'point_name': '6_4_8_analogValue_8', 'index': 9, 'point_writable': 'True', 'point_device_address': '6:4/604', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '8', 'point_description': '', 'objectName': 'Random-604-8', 'presentValue': '8.0'},
                  # '6_4_9_analogValue_9' : {'point_name': '6_4_9_analogValue_9', 'index': 10, 'point_writable': 'True', 'point_device_address': '6:4/604', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '9', 'point_description': '', 'objectName': 'Random-604-9', 'presentValue': '9.0'},
                  # '6_4_10_analogValue_10':  {'point_name': '6_4_10_analogValue_10', 'index': 11, 'point_writable': 'True', 'point_device_address': '6:4/604', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '10', 'point_description': '', 'objectName': 'Random-604-10', 'presentValue': '10.0'}
                  }

    client = BacnetDriver(configs = dict_config, points= dict_point)
    client.read(names=['6_4_1_analogValue_1'])

test_driver()