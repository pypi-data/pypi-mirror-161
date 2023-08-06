import time

from robertcommondriver.system.iot.iot_obix import IOTObix


def logging_print(content):
    print(content)


def test_ping():
    client = IOTObix(configs={'username': 'Monitor', 'password': 'Yorktown123', 'url': 'http://67.200.176.210:8082', 'timeout': 10}, points={})
    print(client.ping())
    print()


def test_get():
    point_dict = {}
    point_dict['test1'] = {'point_name': 'test1', 'point_url': '/obix/config/Drivers/BacnetNetwork/Chiller_2/points/CHW_ENT','point_type': 'real', 'point_writable': False,  'point_description': ''}
    point_dict['test2'] = {'point_name': 'test2', 'point_url': '/obix/config/Drivers/BacnetNetwork/Chiller_2/points/CHW_SPT1','point_type': 'real', 'point_writable': False,  'point_description': ''}
    driver = IOTObix(configs={'username': 'Monitor', 'password': 'Yorktown123', 'url': 'http://67.200.176.210:8081', 'timeout': 10}, points=point_dict)
    while True:
        if driver.ping() == True:
            result = driver.read()  # 读取点
            print(result)
        time.sleep(10)


def test_read():
    points = {'Services_AlarmService_Add': {'point_name': 'Services_AlarmService_Add', 'point_writable': True,
                                            'point_url': '/obix/config/Services/AlarmService/Add/',
                                            'point_type': 'real',
                                            'point_description': '500.0 {ok}', 'point_value': '500.0'},
              'Services_AlarmService_TotalAlarm': {'point_name': 'Services_AlarmService_TotalAlarm',
                                                   'point_writable': True,
                                                   'point_url': '/obix/config/Services/AlarmService/TotalAlarm1/',
                                                   'point_type': 'real', 'point_description': '500.0 {ok} @ 10',
                                                   'point_value': '500.0'},
              'Services_AlarmService_test': {'point_name': 'Services_AlarmService_test', 'point_writable': True,
                                             'point_url': '/obix/config/Services/AlarmService/test/',
                                             'point_type': 'bool',
                                             'point_description': 'false {overridden,unackedAlarm} @ 8',
                                             'point_value': 'false'}}
    driver = IOTObix(configs={'username': 'Monitor', 'password': 'Yorktown123', 'url': 'http://67.200.176.210:8081', 'reltime': 'PT30M', 'filiter': ['obix:Point'], 'timeout': 10}, points=points)
    driver.logging(call_logging=logging_print)
    while True:
        if driver.ping() == True:
            result = driver.read()  # 读取点
            print(result)
        time.sleep(10)


def test_scan():
    driver = IOTObix(configs={'username': 'Monitor', 'password': 'Yorktown123', 'url': 'http://67.200.176.210:8081', 'filiter': ['obix:Point'], 'timeout': 10}, points={})
    driver.logging(call_logging=logging_print)
    if driver.ping() == True:
        result = driver.scan(limit=10)  # 读取点
        print(result)


test_read()