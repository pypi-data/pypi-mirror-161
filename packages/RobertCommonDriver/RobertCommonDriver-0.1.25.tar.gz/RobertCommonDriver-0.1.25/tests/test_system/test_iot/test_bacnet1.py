import time
from robertcommondriver.system.iot.iot_bacnet import IOTBacnet

def logging_print(**kwargs):
    print(kwargs)


def test_scan():

    dict_config = {
        'address': '172.17.164.211/24:47808',  # bacnet server ip(绑定网卡)
        'identifier': 5515,  # bacnet server identifier
        'name': 'BacnetDriver',  # bacnet server name
        'max_apdu': 1024,  # bacnet server max apdu
        'segmentation': 'segmentedBoth',  # bacnet server segmentation
        'vendor_identifier': 15,  # bacnet server vendor
        'multi_read': 20,  # bacnet 批量读取个数
        'cmd_interval': 0.3,  # bacnet命令间隔
        'time_out': 5000  # 超时时间
    }

    points = {'6_4_1_analogValue_1': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True',
                                      'point_device_address': '172.17.30.127', 'point_type': 'analogInput',
                                      'point_property': 'presentValue', 'point_address': 13, 'point_description': '',
                                      'objectName': 'Random-604-1', 'presentValue': '1.0'},
              '6_4_1_analogValue_12': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True',
                                       'point_device_address': '172.17.30.127', 'point_type': 'analogInput',
                                       'point_property': 'presentValue', 'point_address': 12, 'point_description': '',
                                       'objectName': 'Random-604-1', 'presentValue': '1.0'},
              }

    client = IOTBacnet(configs = dict_config, points=points)
    client.logging(call_logging=logging_print)
    print(client.discover())
    results = client.ping(target_address='6:4/604/192.168.1.184')
    # results = client.ping(target_address='172.17.30.127')
    results = client.read(ping_check=False)
    #results = client.scan(target_address='172.17.30.127', ping_check=False)
    # print(client.scan(target_address='6:4/604/192.168.1.184'))
    # print(client.scan())
    print(results)


def test_whois():
    dict_config = {
        'address': '172.17.164.211:47808',  # bacnet server ip(绑定网卡)
        'identifier': 5515,  # bacnet server identifier
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

    cache = {}
    results = client.discover()
    while count != len(results):
        count = len(results)
        time.sleep(30)
        results = client.discover()

        with open(f"bacnet.csv", 'a+') as f:
            for k, v in results.items():
                if k not in cache.keys():
                    cache[k] = 1
                    f.write(f"{k} -- {v}\n")

    print('finish')

test_whois()