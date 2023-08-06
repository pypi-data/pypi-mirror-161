import time
from robertcommondriver.system.iot.iot_iec104 import IOTIEC104


def logging_print(**kwargs):
    print(kwargs)


def test_read():
    dict_config = {'host': '192.168.1.172', 'port': 2404, 'timeout': 4}
    dict_point = {}
    dict_point['iec1'] = {'point_writable': True, 'point_name': 'iec1', 'point_type': 1, 'point_address': 3, 'point_scale': '1'}
    dict_point['iec2'] = {'point_writable': True, 'point_name': 'iec2', 'point_type': 13, 'point_address': 16385, 'point_scale': '1'}

    client = IOTIEC104(configs = dict_config, points= dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            result = client.read(names=list(dict_point.keys()))
            print(result)
        except Exception as e:
            print(f"error: {e.__str__()}")
        time.sleep(4)


test_read()