import time
import random
from robertcommondriver.system.iot.iot_opcda import IOTOPCDA


def logging_print(**kwargs):
    print(kwargs)


def test_read_write():
    dict_config = {
        'server': 'Matrikon.OPC.Simulation.1',
        'host': 'localhost',  # 'host': '192.168.1.36:8804', 192.168.2.131:8810
        'enabled': True,
        'group': f'opcda1',  #
        'action': 'sync',
        'read_limit': 50,
        'update_rate': 500
    }

    dict_point = {}
    dict_point['static_int'] = {'point_writable': True, 'point_name': 'static_int', 'point_tag': '213Bucket Brigade.Int1', 'point_type': '', 'point_description': ''}
    dict_point['static_int1'] = {'point_writable': True, 'point_name': 'static_int1', 'point_tag': 'Bucket Brigade.Int1', 'point_type': '', 'point_description': ''}
    dict_point['random_float'] = {'point_writable': True, 'point_name': 'random_float', 'point_tag': 'Random.Real4', 'point_type': '', 'point_description': ''}
    dict_point['random_str'] = {'point_writable': True, 'point_name': 'random_str', 'point_tag': 'Random.String', 'point_type': '', 'point_description': ''}

    client = IOTOPCDA(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    while True:
        try:
            print(client.ping())
            reuslts = client.read()
            print(reuslts)

            client.write(values={'static_int1': random.randint(1,10), 'static_int': random.randint(1,10)})

            print(client.info())
        except Exception as e:
            client.close()
            print(e.__str__())
        time.sleep(4)


def test_scan():
    dict_config = {
        'server': 'Matrikon.OPC.Simulation.1',
        'host': 'localhost',  # 'host': '192.168.1.36:8804', 192.168.2.131:8810
        'enabled': True,
        'group': f'opcda1',  #
        'read_limit': 50,
        'update_rate': 500
    }

    dict_point = {}

    client = IOTOPCDA(configs=dict_config, points=dict_point)
    client.logging(call_logging=logging_print)
    print(f"ping: {client.ping()}")
    print(f"discover: {client.discover()}")
    result = client.scan(path='*', include_property=True)
    print(f"scan: {result}")
    time.sleep(4)


test_read_write()