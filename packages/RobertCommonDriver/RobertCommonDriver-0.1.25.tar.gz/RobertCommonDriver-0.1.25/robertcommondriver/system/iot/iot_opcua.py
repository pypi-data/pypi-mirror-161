import json
import logging

from opcua import Client, Server, ua
from opcua.common.ua_utils import val_to_string
from opcua.common.callback import CallbackType
from typing import List, Union, Any, Dict

from .base import IOTBaseCommon, IOTDriver, IOTSimulateObject

'''
pip install opcua==0.98.13
'''

logging.getLogger('opcua').setLevel(logging.CRITICAL)


class IOTOPCUA(IOTDriver):

    class SubHandler(object):

        def __init__(self, callbacks: dict):
            self.callbacks = callbacks

        def datachange_notification(self, node, val, data):
            if 'datachange_notification' in self.callbacks.keys():
                self.callbacks['datachange_notification'](node, val, data)

        def event_notification(self, event):
            if 'event_notification' in self.callbacks.keys():
                self.callbacks['event_notification'](event)

        def status_change_notification(self, status):
            if 'status_change_notification' in self.callbacks.keys():
                self.callbacks['status_change_notification'](status)

    class BrowerState:

        def __init__(self, parent, node, deep=0):
            self.parent = parent
            self.node = node
            self.deep = deep

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.reinit()

    def reinit(self):
        self.exit_flag = False
        self.sub_nodes = {}
        self.subs = []
        self.sub = None  # 订阅信息
        self.client = None
        self.server = None
        self.server_ns = 0
        self.server_nodes = {}
        self.server_node_folder = {}

    def exit(self):
        self.exit_flag = True

        self._release_client()

        self._release_server()

        self.reinit()

    @classmethod
    def template(cls, mode: int, type: str, lan: str) -> List[Dict[str, Any]]:
        templates = []
        if type == 'point':
            templates.append({'required': True, 'name': '是否可写' if lan == 'ch' else 'writable'.upper(), 'code': 'point_writable', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''})
            templates.append({'required': True, 'name': '物理点名' if lan == 'ch' else 'name'.upper(), 'code': 'point_name', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''})
            templates.append({'required': True, 'name': 'OPC节点ID' if lan == 'ch' else 'node id'.upper(), 'code': 'point_node_id', 'type': 'string', 'default': 'ns=2;i=13', 'enum': [], 'tip': ''})
            templates.append({'required': False, 'name': 'OPC节点描述' if lan == 'ch' else 'description'.upper(), 'code': 'point_description', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''})
            if mode == 0:
                templates.append({'required': False, 'name': '逻辑点名' if lan == 'ch' else 'name alias'.upper(), 'code': 'point_name_alias', 'type': 'string', 'default': 'Chiller_1_CHW_ENT1', 'enum': [], 'tip': ''})
            else:
                templates.append({'required': True, 'name': 'OPC节点路径' if lan == 'ch' else 'name path'.upper(), 'code': 'point_node_path', 'type': 'string', 'default': 'Chiller 1/CHW ENT 1', 'enum': [], 'tip': ''})
                templates.append({'required': True, 'name': '点值' if lan == 'ch' else 'value'.upper(), 'code': 'point_value', 'type': 'int', 'default': 0, 'enum': [], 'tip': ''})
            templates.append({'required': True, 'name': '是否启用' if lan == 'ch' else 'enable'.upper(), 'code': 'point_enabled', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''})
            templates.append({'required': True, 'name': '倍率' if lan == 'ch' else 'scale'.upper(), 'code': 'point_scale', 'type': 'string', 'default': '1', 'enum': [], 'tip': ''})
        elif type == 'config':
            if mode == 0:
                templates.append({'required': True, 'name': 'OPC服务地址' if lan == 'ch' else 'Endpoint', 'code': 'endpoint', 'type': 'string', 'default': 'opc.tcp://192.168.1.182:4841/freeopcua/server/', 'enum': [], 'tip': ''})
                templates.append({'required': True, 'name': 'OPC超时(s)' if lan == 'ch' else 'TimeOut(s)', 'code': 'timeout', 'type': 'int', 'default': 4, 'enum': [], 'tip': ''})
                templates.append({'required': False, 'name': 'OPC安全' if lan == 'ch' else 'Security', 'code': 'security', 'type': 'string', 'default': '', 'enum': [], 'tip': ''})
                templates.append({'required': False, 'name': 'OPC权限' if lan == 'ch' else 'Auth', 'code': 'auth', 'type': 'string', 'default': '{}', 'enum': [], 'tip': ''})
                templates.append({'required': True, 'name': 'OPC订阅点数限制' if lan == 'ch' else 'Subscript Limit', 'code': 'subscript_add', 'type': 'int', 'default': 1000, 'enum': [], 'tip': ''})
                templates.append({'required': True, 'name': '订阅更新速率(ms)' if lan == 'ch' else 'Subscript Interval(ms)', 'code': 'subscript_interval', 'type': 'int', 'default': 500, 'enum': [], 'tip': ''})
                templates.append({'required': False, 'name': '通道超时(ms)' if lan == 'ch' else 'Channel Timeout(ms)', 'code': 'channel_timeout', 'type': 'int', 'default': 10000, 'enum': [], 'tip': ''})
                templates.append({'required': False, 'name': '会话超时(ms)' if lan == 'ch' else 'Session Timeout(ms)', 'code': 'session_timeout', 'type': 'int', 'default': 10000, 'enum': [], 'tip': ''})
            else:
                templates.append({'required': True, 'name': 'OPC服务地址' if lan == 'ch' else 'Endpoint', 'code': 'endpoint', 'type': 'string', 'default': 'opc.tcp://0.0.0.0:4841/freeopcua/server/', 'enum': [], 'tip': ''})
                templates.append({'required': True, 'name': 'OPC服务名称' if lan == 'ch' else 'Name', 'code': 'name', 'type': 'string', 'default': 'OPCUAServer', 'enum': [], 'tip': ''})
                templates.append({'required': True, 'name': 'OPC根目录' if lan == 'ch' else 'Root', 'code': 'root', 'type': 'string', 'default': 'Robert', 'enum': [], 'tip': ''})
        return templates

    def read(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        results = {}
        names = kwargs.get('names', list(self.points.keys()))

        read_items = []
        for name in names:
            point = self.points.get(name)
            if point:
                node_id = point.get('point_node_id')
                if node_id is not None:
                    if node_id not in self.sub_nodes.keys() and node_id not in read_items:
                        read_items.append(node_id)

        self._read(read_items)

        for name in names:
            point = self.points.get(name)
            if point:
                node_id = point.get('point_node_id')
                if node_id is not None:
                    if self._get_client() is not None:
                        value = self.sub_nodes.get(self.client.get_node(node_id).nodeid.to_string())
                        if value is not None and isinstance(value, list):
                            results[name] = value[0]

        self.update_info(read=len(names), response=len(results))
        return results

    def write(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        results = {}
        values = kwargs.get('values', {})
        for name, value in values.items():
            point = self.points.get(name)
            if point:
                node_id = point.get('point_node_id')
                if node_id is not None:
                    results[name] = self._write(node_id, value)
            else:
                results[name] = [False, 'UnExist']
        return results

    def ping(self, **kwargs) -> bool:
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        if self._get_client() is not None:
            return self._get_client().get_node(ua.ObjectIds.Server_ServerStatus_State).get_value() == 0
        return False

    def scan(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        results = {}
        self.logging(content=f"scan({self.configs.get('endpoint')})")
        if self._get_client() is not None:
            self._brower_child('Root', self._get_client().get_root_node().get_child(["0:Objects"]), -1, ['Server'], results)
        self.update_info(scan=len(results))
        return results

    def discover(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        results = {}
        target = kwargs.get('target', 'opc.tcp://localhost:4840')
        self.logging(content=f"discover({target})")
        client = Client(target)
        for i, ep in enumerate(client.connect_and_get_server_endpoints(), start=1):
            results[f"endpoint_{len(results)}"] = self._endpoint_to_strings(ep)

        self.update_info(discover=len(results))
        return results

    def simulate(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        points = kwargs.get('points', {})
        self.logging(content=f"simulate({len(points)})")
        server_objects = []
        for name, point in points.items():
            point = points.get(name)
            if point:
                node_id = point.get('point_node_id')
                if node_id is not None:
                    server_objects.append(IOTSimulateObject(**point))

        if len(server_objects) > 0:
            if self._get_server() is not None:
                self._create_objects(server_objects)

                self._refresh_objects(server_objects)

    def _get_client(self):
        if self.client is None:
            client = Client(self.configs.get('endpoint'), timeout=self.configs.get('timeout', 4))
            if len(self.configs.get('security', '')) > 0:   # Basic256Sha256,SignAndEncrypt,certificate-example.der,private-key-example.pem
                client.set_security_string(self.configs.get('security', ''))
            auth = self.configs.get('auth', {})
            if isinstance(auth, str) and len(auth) >= 0:
                auth = json.loads(auth)
            if 'type' in auth.keys():
                if auth['type'] == 'UserName':
                    client.set_user(auth['user'])
                    client.set_password(auth['password'])
                elif auth['type'] == 'Certificate':
                    client.load_client_certificate(auth['client_certificate'])
                    client.load_private_key(auth['private_key'])

            client.secure_channel_timeout = self.configs.get('channel_timeout', 10000)
            client.session_timeout = self.configs.get('session_timeout', 10000)

            client.connect()
            client.load_type_definitions()

            # IOTBaseCommon.function_thread(embed, True).start()

            self.client = client
        else:
            try:
                self.client.send_hello()
            except Exception as e:
                print(e.__str__())
                self._release_client()
        return self.client

    def _release_client(self):
        try:
            if self.client is not None:
                if self.sub is not None:
                    for sub in self.subs:
                        self.sub.unsubscribe(sub)
                    self.sub.delete()
                self.client.disconnect()
        except:
            pass
        self.client = None

    def _get_sub(self):
        if self.sub is None:
            sub = self._get_client().create_subscription(self.configs.get('subscript_interval', 500), self.SubHandler(callbacks={'datachange_notification': self._datachange_notification}))
            self.sub = sub
        return self.sub

    def _brower_child(self, parent, node, max_deep: int, ignore: list, results: dict):
        stack = [self.BrowerState(parent, node, 0)]
        while len(stack) > 0:
            if self._get_client() is not None:
                current = stack.pop()
                class_name = current.node.get_node_class().name

                browse_name = current.node.get_browse_name().Name
                if browse_name in ignore:
                    continue

                path = f"{current.parent}/{browse_name}"

                if class_name == "Object":
                    if max_deep > 0 and current.deep >= max_deep:
                        continue
                    for c in current.node.get_children():
                        stack.append(self.BrowerState(path, c, current.deep + 1))
                elif class_name == 'Variable':
                    attributes = current.node.get_attributes([ua.AttributeIds.Description, ua.AttributeIds.NodeId, ua.AttributeIds.DataType, ua.AttributeIds.Value])
                    desc, nid, dtype, val = [attr.Value.Value for attr in attributes]
                    point_name = IOTBaseCommon.format_name(path)
                    results[point_name] = self.create_point(point_name=point_name, point_name_alias=point_name, point_node_id=nid.to_string(), point_node_path=path, point_value=str(val_to_string(val)), point_description='' if desc is None else desc.to_string())
                    self.logging(content=f"scan {len(results)} point({path})")

    def _datachange_notification(self, node, val, data):
        try:
            if data.monitored_item.Value.StatusCode.is_good():
                if val is not None:
                    self.sub_nodes[node.nodeid.to_string()] = [str(val_to_string(val)), IOTBaseCommon.get_datetime_str()]
        except Exception as e:
            logging.error(f"datachange fail({e.__str__()})")

    def _create_monitored_items(self, event, dispatcher):
        for idx in range(len(event.response_params)):
            if (event.response_params[idx].StatusCode.is_good()):
                nodeId = event.request_params.ItemsToCreate[idx].ItemToMonitor.NodeId
                # print("Node {0} was created".format(nodeId))

    def _modify_monitored_items(self, event, dispatcher):
        pass  # print('modify_monitored_items')

    def _delete_monitored_items(self, event, dispatcher):
        pass  # print('delete_monitored_items')

    def _read(self, read_items: list):
        if len(read_items) > 0:
            if self._get_client():
                items = []
                for item in read_items:
                    node = self._get_client().get_node(item)
                    if node:
                        items.append((item, node))
                nodes = IOTBaseCommon.chunk_list(items, self.configs.get('subscript_add', 1000))
                if self._get_sub() is not None:
                    for _nodes in nodes:
                        subs = [node for id, node in _nodes]
                        ids = [id for id, node in _nodes]
                        sub_nodes = self._get_sub().subscribe_data_change(subs)
                        for index, sub_node in enumerate(sub_nodes):
                            if isinstance(sub_node, ua.StatusCode):
                                logging.error(f"read ({ids[index]}) fail({sub_node.name})")
                            else:
                                self.logging(content=f"add subscribe success({sub_node})")
                                self.subs.append(sub_node)
                        self.sub_nodes.update(dict.fromkeys(ids, None))

    def _write(self, node, value):
        try:
            if self._get_client():
                self._get_client().get_node(node).set_value(ua.Variant(value))
                node.set_value(ua.Variant(value))
                return [True, '']
        except Exception as e:
            return [False, e.__str__()]
        return [False, 'Unknown']

    def _get_server(self):
        if self.server is None:
            server = Server()
            server.set_endpoint(self.configs.get('endpoint'))
            server.set_server_name(self.configs.get('name', 'Robert OPC UA Server'))
            # 设置客户端连接的所有可能端点策略
            server.set_security_policy([
                ua.SecurityPolicyType.NoSecurity,
                ua.SecurityPolicyType.Basic128Rsa15_SignAndEncrypt,
                ua.SecurityPolicyType.Basic128Rsa15_Sign,
                ua.SecurityPolicyType.Basic256_SignAndEncrypt,
                ua.SecurityPolicyType.Basic256_Sign])

            # 设置我们自己的命名空间
            ns = server.register_namespace('Robert_OPCUA_Server')

            server.start()

            # 为项目事件创建回调
            server.subscribe_server_callback(CallbackType.ItemSubscriptionCreated, self._create_monitored_items)
            server.subscribe_server_callback(CallbackType.ItemSubscriptionModified, self._modify_monitored_items)
            server.subscribe_server_callback(CallbackType.ItemSubscriptionDeleted, self._delete_monitored_items)

            self.server = server
            self.server_ns = ns
        return self.server

    def _release_server(self):
        try:
            if self.server is not None:
                self.server.stop()
        except Exception as e:
            pass
        self.server = None

    def _create_folder(self, server, paths: Union[str, list]):
        root_folder = self.server_node_folder[self.configs.get('root', 'Robert')]
        if isinstance(paths, list):
            for index, folder in enumerate(paths):
                self._create_folder(server, '/'.join(paths[:index+1]))
        elif isinstance(paths, str):
            self.server_node_folder[paths] = self.server_node_folder.get(IOTBaseCommon.get_file_folder(paths), root_folder).add_object(f"ns=2;i={len(self.server_node_folder) + 10}", IOTBaseCommon.get_file_name(paths))
        return self.server_node_folder.get('/'.join(paths), root_folder)

    def _create_objects(self, objects: List[IOTSimulateObject]):
        root = self.configs.get('root', 'Robert')
        if root not in self.server_node_folder.keys():
            self.server_node_folder[root] = self._get_server().get_objects_node().add_folder(self.server_ns, root)

        for object in objects:
            node_id = object.get('point_node_id')
            if node_id not in self.server_nodes.keys():
                node_path = object.get('point_node_path', '')
                if len(node_path) > 0:
                    try:
                        paths = node_path.split('/')
                        folder = self._create_folder(self._get_server(), paths[:-1])
                        self.server_nodes[node_id] = folder.add_variable(node_id, paths[-1], IOTBaseCommon.format_value(object.get('point_value')))
                        self.server_nodes[node_id].set_writable()
                    except Exception as e:
                        logging.error(f"create object({node_id} {node_path}) fail({e.__str__()})")

    def _refresh_objects(self, objects: List[IOTSimulateObject]):
        for object in objects:
            node_id = object.get('point_node_id')
            if node_id in self.server_nodes.keys():
                try:
                    self.server_nodes[node_id].set_value(IOTBaseCommon.format_value(object.get('point_value')))
                except Exception as e:
                    logging.error(f"refresh object({node_id}) fail({e.__str__()})")

    def _cert_to_string(self, der):
        if not der:
            return 'no certificate'
        try:
            from opcua.crypto import uacrypto
        except ImportError:
            return "{0} bytes".format(len(der))
        cert = uacrypto.x509_from_der(der)
        return uacrypto.x509_to_string(cert)

    def _endpoint_to_strings(self, ep):
        properties = {}
        properties['endpoint'] = ep.EndpointUrl
        properties['name'] = ep.Server.ApplicationName.to_string()
        properties['type'] = str(ep.Server.ApplicationType)
        for url in ep.Server.DiscoveryUrls:
            properties['discovery url'] = url
        properties['certificate'] = self._cert_to_string(ep.ServerCertificate)
        properties['security mode'] = str(ep.SecurityMode)
        properties['certificate'] = ep.SecurityPolicyUri
        properties[f'user policy'] = {}
        for tok in ep.UserIdentityTokens:
            properties[f'user policy'][str(tok.TokenType)] = tok.PolicyId

            if tok.SecurityPolicyUri:
                properties[f'user policy']['uri'] = tok.SecurityPolicyUri
        properties[f'security level'] = ep.SecurityLevel
        return properties