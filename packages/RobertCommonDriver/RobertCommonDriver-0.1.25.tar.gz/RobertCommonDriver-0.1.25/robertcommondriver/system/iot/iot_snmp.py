
import logging

from typing import List, Dict, Any
from pysnmp.hlapi import *
from .base import IOTBaseCommon, IOTDriver

'''
pip install pysnmp==4.4.12
'''


class IOTSNMP(IOTDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def reinit(self):
        self.exit_flag = False

    def exit(self):
        self.exit_flag = True

    @classmethod
    def template(cls, mode: int, type: str, lan: str) -> List[Dict[str, Any]]:
        templates = []
        if type == 'point':
            templates.extend([
                    {'required': True, 'name': '是否可写' if lan == 'ch' else 'writable'.upper(), 'code': 'point_writable', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                    {'required': True, 'name': '物理点名' if lan == 'ch' else 'name'.upper(), 'code': 'point_name', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''},
                    {'required': True, 'name': '设备地址' if lan == 'ch' else 'Address', 'code': 'point_device_address', 'type': 'string', 'default': '192.168.1.200/161/v1/public/private', 'enum': [], 'tip': ''},
                    {'required': True, 'name': 'OID' if lan == 'ch' else 'oid'.upper(), 'code': 'point_oid', 'type': 'string', 'default': '1.3.6.1.2.1.1.1.0', 'enum': [], 'tip': ''},
                    {'required': False, 'name': '点描述' if lan == 'ch' else 'description'.upper(), 'code': 'point_description', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''},
                    {'required': False, 'name': '逻辑点名' if lan == 'ch' else 'name alias'.upper(), 'code': 'point_name_alias', 'type': 'string', 'default': 'Chiller_1_CHW_ENT1', 'enum': [], 'tip': ''},
                    {'required': True, 'name': '是否启用' if lan == 'ch' else 'enable'.upper(), 'code': 'point_enabled', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                    {'required': True, 'name': '倍率' if lan == 'ch' else 'scale'.upper(), 'code': 'point_scale', 'type': 'string', 'default': '1', 'enum': [], 'tip': ''}
            ])
        elif type == 'config':
            templates.extend([
                    {'required': True, 'name': '超时(s)' if lan == 'ch' else 'Cmd Timeout(s)', 'code': 'cmd_timeout', 'type': 'int', 'default': 3, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '重试' if lan == 'ch' else 'Cmd Retries', 'code': 'cmd_retries', 'type': 'int', 'default': 3, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '批量读取个数' if lan == 'ch' else 'Multi Read', 'code': 'multi_read', 'type': 'int', 'default': 20, 'enum': [], 'tip': ''},
                    {'required': True, 'name': '命令间隔(s)' if lan == 'ch' else 'Cmd Interval(s)', 'code': 'cmd_interval', 'type': 'float', 'default': 0.3, 'enum': [], 'tip': ''}
            ])

        return templates

    def read(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        results = {}
        names = kwargs.get('names', list(self.points.keys()))
        read_items = {}
        for name in names:
            point = self.points.get(name)
            if point:
                oid = point.get('point_oid')
                device_host = point.get('point_device_address')    # 192.168.1.200/161/v1/public/private
                if oid is not None and device_host is not None:
                    if device_host not in read_items.keys():
                        read_items[device_host] = [[]]
                    if len(read_items[device_host][-1]) >= self.configs.get('multi_read'):
                        read_items[device_host].append([])
                    read_items[device_host][-1].append(ObjectType(ObjectIdentity(oid)))

        datas = self._read(read_items)

        for name in names:
            point = self.points.get(name)
            if point:
                oid = point.get('point_oid')
                if oid is not None:
                    value = datas.get(oid)
                    if value is not None:
                        results[name] = value

        self.update_info(read=len(names), response=len(results))
        return results

    def write(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        results = {}
        values = kwargs.get('values', {})
        for name, value in values.items():
            point = self.points.get(name)
            if point:
                oid = point.get('point_oid')
                device_host = point.get('point_device_address')  # 192.168.1.200/161/v1/public/private
                if oid is not None and device_host is not None:
                    results[name] = self._write(device_host, oid, value)
            else:
                results[name] = [False, 'UnExist']
        return results

    def ping(self, **kwargs) -> bool:
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        return self._ping(kwargs.get('host'), port=kwargs.get('port', 161), comunity=kwargs.get('comunity', 'public'))

    def discover(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        networks = IOTBaseCommon.get_networks(kwargs.get('address'))
        self.logging(content=f"discover({kwargs.get('address')})")
        jobs = IOTBaseCommon.SimpleThreadPool(kwargs.get('limit', 40))
        for ip in networks:
            jobs.submit_task(self._discover, host=ip)
        results = jobs.done(False)
        self.update_info(discover=len(results))
        return results

    def scan(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        results = {}
        address = kwargs.get('address')
        root = kwargs.get('root', '1.3')
        self.logging(content=f"scan({address}) {root}")
        try:
            auth, transport, context = self._get_connect_info(address)
            for (error, status, index, var_binds) in bulkCmd(SnmpEngine(), auth, transport, context, 0, 25, ObjectType(ObjectIdentity(root)), lookupMib=False, lexicographicMode=False, ignoreNonIncreasingOid=True):
                if error:
                    logging.error(f"scan({address}) fail({error})")
                    break
                if not status:
                    for var_bind in var_binds:
                        name = IOTBaseCommon.format_name(var_bind[0].prettyPrint())
                        value = var_bind[1].prettyPrint()
                        type = var_bind[1].__class__.__name__
                        results[name] = self.create_point(point_name=name, point_name_alias=name, point_device_address=address, point_oid=name, point_type=type, point_description=name, point_value=value)
                        self.logging(content=f"recv {len(results)} point({name})")
        except Exception as e:
            logging.error(f"scan ({address}) fail({e.__str__()})")
        self.update_info(scan=len(results))
        return results

    def _discover(self, **kwargs):
        return kwargs.get('host') if self._ping(kwargs.get('host'), port=kwargs.get('port', 161), comunity=kwargs.get('comunity', 'public')) else None

    def _ping(self, host: str, port: int = 161, comunity: str = 'public', timeout: float=1, retries: int = 0) -> bool:
        self.logging(content=f"ping {host}:{port} {comunity}")
        error, status, index, var_binds = next(
            getCmd(SnmpEngine(),
                   CommunityData(comunity, mpModel=0),
                   UdpTransportTarget((host, port), timeout=timeout, retries=retries),
                   ContextData(),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0)),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysUpTime', 0)),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysLocation', 0)),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysContact', 0)),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysObjectID', 0)),
                   )
        )
        if not error and not status:
            return True
        return False

    def _read(self, read_items: dict):
        if len(read_items) > 0:
            jobs = IOTBaseCommon.SimpleThreadPool(len(read_items))
            for address, oids in read_items.items():
                jobs.submit_task(self._read_oids, address, oids)
            return jobs.done()
        return {}

    def _get_connect_info(self, address: str):
        infos = address.split('/')  # '192.168.1.200/161/v1/public/private'
        if len(infos) >= 5:
            transport = UdpTransportTarget((infos[0], int(infos[1])), timeout=self.configs.get('cmd_timeout', 3), retries=self.configs.get('cmd_retries', 3))
            context = ContextData()
            if infos[2] == 'v1':
                auth = CommunityData(infos[3], infos[4], mpModel=0)
            elif infos[2] == 'v2':
                auth = CommunityData(infos[3], infos[4], mpModel=1)
            else:
                raise Exception(f"unsupport protocol({infos[2]})")
            return auth, transport, context
        raise Exception(f"invalid address({address})")

    def _read_oids(self, *args, **kwargs):
        (address, oids ) = args
        results = {}
        for oid in oids:
            var_binds = tuple(oid)
            self.logging(content=f"read({address}) oids({len(oid)})")
            auth, transport, context = self._get_connect_info(address)
            error, status, index, var_binds = next(getCmd(SnmpEngine(), auth, transport, context, *var_binds))
            if error:
                logging.error(f"read oids fail({error})")
            elif status:
                logging.error(f"read oids fail({status.prettyPrint()} at {index and var_binds[int(index) - 1][0] or '?'})")
            else:
                for var_bind in var_binds:
                    results[str(var_bind[0])] =  var_bind[1].prettyPrint()
            self.delay(self.configs.get('cmd_interval', 1))
        return results

    def _write(self, address: str, oid: str, value):
        result = [False, '']
        try:
            if len(oid) > 0:
                self.logging(content=f"write({address}) oid({oid})")
                var_binds = tuple([ObjectType(ObjectIdentity(oid), value)])
                auth, transport, context = self._get_connect_info(address)
                error, status, index, var_binds = next(setCmd(SnmpEngine(), auth, transport, context, *var_binds))
                if error:
                    logging.error(f"write oids fail({error})")
                elif status:
                    logging.error(f"write oids fail({status.prettyPrint()} at {index and var_binds[int(index) - 1][0] or '?'})")
                else:
                    result[0] = True
            raise Exception('set fail')
        except Exception as e:  # other
            logging.error(f"plc({address}) write({oid}) fail({e.__str__()})")
            result[1] = e.__str__()
        return result