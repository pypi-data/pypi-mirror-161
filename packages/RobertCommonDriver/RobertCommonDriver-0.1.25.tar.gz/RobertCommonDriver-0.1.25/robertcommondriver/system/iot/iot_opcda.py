
import logging
import os
import Pyro4
import platform
import re
import sys
import time

from datetime import datetime
from typing import Optional, Union, List, Dict, Any
from threading import Event

from .base import IOTBaseCommon, IOTDriver


if platform.system().lower() == 'windows':
    import pywintypes
    import pythoncom
    import win32com.client
    pywintypes.datetime = pywintypes.TimeType
    vt = dict([(pythoncom.__dict__[vtype], vtype) for vtype in pythoncom.__dict__.keys() if vtype[:2] == "VT"])
    win32com.client.gencache.is_readonly = False    # Allow gencache to create the cached wrapper objects
    win32com.client.gencache.Rebuild(verbose=0) # Under p2exe the call in gencache to __init__() does not happen so we use Rebuild() to force the creation of the gen_py folder


class OPCDA:

    @Pyro4.expose
    class OPCClient:

        class GroupEvents:
            def __init__(self):
                self.client = None

            def set_client(self, client):
                self.client = client

            def OnDataChange(self, TransactionID, NumItems, ClientHandles, ItemValues, Qualities, TimeStamps):
                if self.client and hasattr(self.client, 'callback_data_change_value'):
                    self.client.callback_data_change_value('OnDataChange', TransactionID, NumItems, ClientHandles, ItemValues, Qualities, TimeStamps)

            def OnAsyncReadComplete(self, TransactionID, NumItems, ClientHandles, ItemValues, Qualities, TimeStamps, Errors):
                if self.client and hasattr(self.client, 'callback_data_change_value'):
                    self.client.callback_data_change_value('OnAsyncReadComplete', TransactionID, NumItems, ClientHandles, ItemValues, Qualities, TimeStamps, Errors)

            def OnAsyncWriteComplete(self, TransactionID, NumItems, ClientHandles, Errors):
                if self.client and hasattr(self.client, 'callback_data_change_value'):
                    self.client.callback_data_change_value('OnAsyncWriteComplete', TransactionID, NumItems, ClientHandles, None, None, None, Errors)

            def OnAsyncCancelComplete(self, CancelID):
                # Not working, not in VB either
                pass

        class ServerEvents:

            def __init__(self):
                self.client = None

            def set_client(self, client):
                self.client = client

            def OnServerShutDown(self, Reason):
                if self.client and hasattr(self.client, 'callback_shut_down'):
                    self.client.callback_shut_down(Reason)

        def __init__(self, opc_class: Optional[str] = None, client_name: Optional[str] = None, **kwargs):
            pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)

            self.kwargs = kwargs
            self.opc_client = None
            self.opc_name = ''
            self.opc_svc_host = None
            self.opc_svc_port = None
            self.opc_timeout = kwargs.get('timeout', 10)

            self.opc_connected = False
            self.parent = None

            self.opc_class = opc_class if opc_class is not None else os.environ.get('OPC_DA_CLASS', 'Matrikon.OPC.Automation;Graybox.OPC.DAWrapper;HSCOPC.Automation;RSI.OPCAutomation;OPC.Automation')
            self.opc_client_name = client_name if client_name is not None else os.getenv('OPC_DA_CLIENT', 'OPCDA_CLIENT')

            self.data_source = {'cache': 1, 'device': 2}
            self.opc_status = (0, 'Running', 'Failed', 'NoConfig', 'Suspended', 'Test')
            self.browser_types = (0, 'Hierarchical', 'Flat')
            self.access_rights = (0, 'Read', 'Write', 'Read/Write')
            self.opc_qualitys = ('Bad', 'Uncertain', 'Unknown', 'Good')

            ############
            self.opc_info = {}

            self.opc_groups = {}  # 组
            self.opc_group_transaction_id = {}  # 订阅ID对应事件
            self.opc_client_handle = 0
            self.opc_client_handle_value = {}  # handle: value
            self.opc_items = {} # tag client
            self.opc_logs = []

            # service
            self.opc_svc_guid = None
            self.opc_svc = None
            self.opc_svc_client = None
            self.opc_transaction_id = 0
            self.opc_prev_serv_time = None

            self._update_info(start=IOTBaseCommon.get_timestamp(), pid=IOTBaseCommon.get_pid())

        def __del__(self):
            self.exit()

        def exit(self):
            pythoncom.CoUninitialize()
            self.close(True)

        def set_parent(self, parent):
            self.parent = parent

        def save_log(self, log_content: str):
            if isinstance(log_content, str) and len(log_content) > 0:
                if len(self.logs) >= 500:
                    self.logs.pop(0)
                self.logs.append((log_content))

        def logging(self, **kwargs):
            if self.parent and hasattr(self.parent, 'logging'):
                self.parent.logging(**kwargs)

        def set_svc_info(self, host: str, port: int, guid: str, client, service):
            self.opc_svc_guid = guid
            self.opc_svc = service
            self.opc_svc_client = client
            self.opc_svc_host = host
            self.opc_svc_port = port
            self._update_info(guid=guid)

        #####interface###########
        def get_info(self):
            return self.opc_info

        def is_connected(self):
            return self.opc_connected

        def connect(self, name: Optional[str] = None, host: str = 'localhost') -> bool:
            if self.opc_connected is False:
                self._update_info(used=time.time(), name=name, host=host)
                self.logging(content=f"connect({name} - {host})")

                self._get_client().Connect(name, host)

                self.opc_name = name
                self.opc_svc_host = host
                self.opc_connected = True
                self._update_info(connected=self.opc_connected)

                self.reset()
            return self.opc_connected

        def guid(self):
            return self.opc_svc_guid

        def disconnect(self):
            self._update_info(used=time.time(), connected=self.opc_connected)
            self.logging(content=f"disconnect")
            if self.opc_client is not None:
                self.opc_client.Disconnect()

        def close(self, del_object: bool = True):
            self._update_info(used=time.time())
            self.logging(content=f"close({del_object})")

            opc_connected = self.opc_connected
            try:
                self.opc_connected = False
                self._remove_groups(self.groups(), opc_connected)
                if opc_connected is True:
                    self.disconnect()
            except pythoncom.com_error as err:
                logging.error(f"close fail({self._get_error(err)})")
            except Exception as e:
                logging.error(f"close fail({e.__str__()})")
            finally:
                # Remove this object from the open gateway service
                if self.opc_svc and del_object:
                    self.opc_svc.release_client(self.opc_svc_client)
                    self.opc_svc_client = None

        def groups(self) -> list:
            self._update_info(used=time.time())
            return sorted(list(self.opc_groups.keys()))

        def add_group(self, group_name: str, update_rate: int = 1000) -> bool:
            if group_name not in self.opc_groups.keys():
                self._update_info(used=time.time(), group=group_name)
                self.logging(content=f"add group({group_name})")
                try:
                    opc_groups = self.opc_client.OPCGroups
                    opc_group = opc_groups.Add(group_name)
                    opc_group.IsSubscribed = 1
                    opc_group.IsActive = 1
                    opc_group.DeadBand = 0
                    opc_group.UpdateRate = update_rate

                    group_event = win32com.client.WithEvents(opc_group, self.GroupEvents)
                    group_event.set_client(self)

                    self._update_group_info(group_name, group=opc_group, group_event=group_event)
                except pythoncom.com_error as err:
                    raise Exception(f"add group({group_name}) fail({self._get_error(err)})")
            return True

        def remove_group(self, group_name: str):
            self._update_info(used=time.time(), group=None)
            self.logging(content=f"remove group({group_name})")

            if self.opc_client is not None:
                self.opc_client.OPCGroups.Remove(group_name)

        def add_items(self, group_name: str, item_tags: list):
            self._update_info(used=time.time())
            if group_name in self.opc_groups.keys():
                tags, single, valid = self._type_check(item_tags)
                if valid is False:
                    raise Exception(f"tags must be a string or a list of strings")

                new_tags = []
                for item_tag in item_tags:
                    if self._check_item_exist(group_name, item_tag) is False:
                        new_tags.append(item_tag)

                valid_tags = []
                client_handles = []
                error_msgs = {}

                group_tags = self._get_group_info(group_name, 'tags', {})

                if len(new_tags) > 0:
                    errors = self._check_items(group_name, new_tags.copy())

                    for i, item_tag in enumerate(new_tags):
                        if errors[i] == 0:
                            valid_tags.append(item_tag)
                            self.opc_client_handle = self.opc_client_handle + 1
                            group_tags[item_tag] = self.opc_client_handle
                            client_handles.append(self.opc_client_handle)
                        else:
                            error_msgs[item_tag] = self.opc_client.GetErrorString(errors[i])

                    self._update_group_info(group_name, tags=group_tags)
                    self._update_info(tags=len(group_tags))

                    if len(valid_tags) > 0:
                        self.logging(content=f"add group({group_name}) item({len(valid_tags)})")
                        server_handles, errors = self._add_items(group_name, client_handles.copy(), valid_tags.copy())
                        if len(server_handles) > 0:
                            valid_tags_tmp = []
                            server_handles_tmp = []

                            group_tags_handles = self._get_group_info(group_name, 'tags_handles', {})

                            for i, tag in enumerate(valid_tags):
                                if errors[i] == 0:
                                    valid_tags_tmp.append(tag)
                                    server_handles_tmp.append(server_handles[i])
                                    group_tags_handles[tag] = server_handles[i]
                                else:
                                    error_msgs[tag] = self.opc_client.GetErrorString(errors[i])

                            self._update_group_info(group_name, tags_handles=group_tags_handles)
                            return True if len(valid_tags_tmp) > 0 else False, valid_tags_tmp, error_msgs  # 只要有一个点添加成功即为正确
                        return False, [], dict.fromkeys(item_tags, 'add item fail')  # 添加点失败
                    return False, [], error_msgs  # 点都不正确
                return True, [], {}  # 无需额外添加点
            return False, [], dict.fromkeys(item_tags, 'group not exist')  # 组不存在

        def remove_items(self, group_name: str, item_tags: list):
            self._update_info(used=time.time())
            self.logging(content=f"remove group({group_name}) items({len(item_tags)})")

            if group_name in self.opc_groups.keys():
                tags, single, valid = self._type_check(item_tags)
                if not valid:
                    raise Exception(f"tags must be a string or a list of strings")

                new_tags = []
                for item_tag in item_tags:
                    if self._check_item_exist(group_name, item_tag) is True:
                        new_tags.append(item_tag)

                if len(new_tags) > 0:
                    server_handles = []

                    group_tags_handles = self._get_group_info(group_name, 'tags_handles', {})

                    for item_tag in new_tags:
                        if item_tag in group_tags_handles.keys():
                            server_handles.append(group_tags_handles[item_tag])

                    if len(server_handles) > 0:
                        server_handles.insert(0, 0)
                        self._remove_items(group_name, server_handles)

                    group_tags = self._get_group_info(group_name, 'tags', {})

                    for item_tag in new_tags:
                        if item_tag in group_tags_handles.keys():
                            del group_tags_handles[item_tag]
                        if item_tag in group_tags.keys():
                            del group_tags[item_tag]

                    self._update_info(tags=group_tags)

        def get_datetime_str(self) -> str:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        def callback_data_change_value(self, action: str, transaction_id: int, item_num: int, client_handles: list, values: list, qualities: list, timestamps: list, errors: Optional[list] = None):
            if action in ['OnDataChange', 'OnAsyncReadComplete']:
                now_str = self.get_datetime_str()
                for i in range(item_num):
                    error = ''
                    if errors is not None and i < len(errors) and errors[i] != 0:
                        error = self.opc_client.GetErrorString(errors[i])
                    self._update_values(client_handles[i], values[i], qualities[i], timestamps[i], error, now_str)

            if transaction_id == 0:
                self._update_info(data_change=time.time())

            transaction = self.opc_group_transaction_id.get(transaction_id)
            if transaction is not None:
                transaction.set() # 激活事件

        def callback_shut_down(self, reason):
            self.opc_connected = False
            content = f"Server Shutdown({reason}) at {self.get_datetime_str()}"
            self.logging(content=content)
            logging.error(content)

        def sync_read(self, group_name: str, data_source: int, server_handles: dict):
            self._update_info(used=time.time())


            opc_group = self.opc_groups.get(group_name, {}).get('group')
            if opc_group is not None:
                try:
                    item_tags = list(server_handles.keys())
                    server_handles_ = list(server_handles.values())
                    server_handles_.insert(0, 0)
                    values, errors, qualities, timestamps = opc_group.SyncRead(data_source, len(server_handles_) - 1, server_handles_)
                    success = self._parse_value(group_name, item_tags, values, errors, qualities, timestamps)
                    self.logging(content=f"sync read group({group_name}) ({success}/{len(server_handles)})")
                except pythoncom.com_error as err:
                    raise Exception(f"sync read group({group_name}) fail({self._get_error(err)})")
            else:
                raise Exception(f"sync read group({group_name}) fail(not exist)")

        def _get_transaction_id(self) -> int:
            self.opc_transaction_id = self.opc_transaction_id + 1
            return self.opc_transaction_id

        def async_read(self, group_name: str, server_handles: dict):
            self._update_info(used=time.time())
            self.logging(content=f"async read group({group_name}) {len(server_handles)}")

            opc_group = self.opc_groups.get(group_name, {}).get('group')
            if opc_group is not None:
                try:
                    opc_transaction_id = self._get_transaction_id()
                    self.opc_group_transaction_id[opc_transaction_id] = Event()

                    server_handles_ = list(server_handles.values())
                    server_handles_.insert(0, 0)
                    opc_group.AsyncRead(len(server_handles_) - 1, server_handles_, pythoncom.Missing, self.opc_transaction_id)
                    if not self.opc_group_transaction_id[opc_transaction_id].wait(self.opc_timeout):
                        raise Exception(f"async read group({group_name}) fail(Timeout)")
                except pythoncom.com_error as err:
                    raise Exception(f"async read group({group_name}) fail({self._get_error(err)})")
                finally:
                    del self.opc_group_transaction_id[opc_transaction_id]
            else:
                raise Exception(f"async read group({group_name}) fail(not exist)")

        def async_refresh(self, group_name: str, data_source: int):
            self._update_info(used=time.time())
            self.logging(content=f"async refresh group({group_name})")

            opc_group = self.opc_groups.get(group_name, {}).get('group')
            if opc_group is not None:
                try:
                    opc_transaction_id = self._get_transaction_id()
                    self.opc_group_transaction_id[opc_transaction_id] = Event()
                    opc_group.AsyncRefresh(data_source, self.opc_transaction_id)
                    if not self.opc_group_transaction_id[opc_transaction_id].wait(self.opc_timeout):
                        raise Exception(f"async refresh group({group_name}) fail(Timeout)")
                except pythoncom.com_error as err:
                    raise Exception(f"async refresh group({group_name}) fail({self._get_error(err)})")
                finally:
                    del self.opc_group_transaction_id[opc_transaction_id]
            else:
                raise Exception(f"async refresh group({group_name}) fail(not exist)")

        def read(self, group_name: str, item_tags: Optional[list] = None, action: str = '', source: str = 'cache', size: int = 100, interval: float = 0.1) -> dict:
            self._update_info(used=time.time())

            results = {}
            if self.opc_connected is True:
                item_tags = [] if item_tags is None else item_tags
                if len(item_tags) > 0:
                    result, success, errors = self.add_items(group_name, item_tags)
                    if len(errors) > 0:
                        results.update(errors)
                    if len(success) > 0:
                        action = 'sync'

                valid_item_tags = []
                if len(item_tags) > 0:
                    for item_tag in item_tags:
                        if self._check_item_exist(group_name, item_tag) is True:
                            valid_item_tags.append(item_tag)
                else:
                    opc_group_tags = self.opc_groups.get(group_name, {}).get('tags', {})
                    for item_tag in opc_group_tags.keys():
                        valid_item_tags.append(item_tag)

                #
                if action == 'refresh':  # async异步刷新
                    results.update(self._read(group_name, valid_item_tags, action, source))
                else:
                    item_tags_groups = self._split_to_list(valid_item_tags, size)
                    for item_tags in item_tags_groups:
                        results.update(self._read(group_name, item_tags, action, source))
                        time.sleep(interval)
            else:
                raise Exception(f"{self.opc_name} not connected")
            return results

        def sync_write(self, group_name: str, server_handles: list, item_values: list, item_tags: list):
            self._update_info(used=time.time())
            self.logging(content=f"sync write group({group_name}) ({len(server_handles)})")

            results = {}
            try:
                opc_group = self.opc_groups.get(group_name, {}).get('group')
                if opc_group is not None:
                    try:
                        server_handles.insert(0, 0)
                        item_values.insert(0, 0)
                        errors = opc_group.SyncWrite(len(server_handles) - 1, server_handles, item_values)
                        for i, item_tag in enumerate(item_tags):
                            if errors[i] == 0:
                                results[item_tag] = [True, '']
                            else:
                                results[item_tag] = [False, self._get_error(errors[i])]
                    except pythoncom.com_error as err:
                        raise Exception(f'sync write group({group_name}) fail({self._get_error(err)})')
                else:
                    raise Exception(f"sync write group({group_name}) fail(no group)")
            except Exception as e:
                for item_tag in item_tags:
                    results[item_tag] = [False, e.__str__()]
            return results

        def async_write(self, group_name: str, server_handles: list, item_values: list, item_tags: list):
            self._update_info(used=time.time())
            self.logging(content=f"async write group({group_name}) {len(server_handles)}")

            results = {}
            try:
                opc_group = self.opc_groups.get(group_name, {}).get('group')
                if opc_group is not None:
                    try:
                        server_handles.insert(0, 0)
                        item_values.insert(0, 0)

                        opc_transaction_id = self._get_transaction_id()
                        self.opc_group_transaction_id[opc_transaction_id] = Event()
                        opc_group.AsyncWrite(len(server_handles) - 1, server_handles, item_values, pythoncom.Missing, self.opc_transaction_id)
                        for item_tag in item_tags:
                            results[item_tag] = [True, '']
                        if not self.opc_group_transaction_id[opc_transaction_id].wait(self.opc_timeout):
                            raise Exception(f"async write group({group_name}) fail(Timeout)")
                    except pythoncom.com_error as err:
                        raise Exception(f'async write group({group_name})({self._get_error(err)})')
                    finally:
                        del self.opc_group_transaction_id[opc_transaction_id]
                else:
                    raise Exception(f"async write group({group_name})(no group)")
            except Exception as e:
                for item_tag in item_tags:
                    results[item_tag] = [False, e.__str__()]
            return results

        def write(self, group_name: str, items_values: dict, action: str = 'sync', size: int = 100, interval: float = 0.1) -> dict:
            self._update_info(used=time.time())

            results = {}
            if self.opc_connected is True:
                if len(items_values) > 0:
                    result, success, errors = self.add_items(group_name, list(items_values.keys()))
                    if len(errors) > 0:
                        for k, v in errors.items():
                            results[k] = [False, v]
                    if len(success) > 0:
                        action = 'sync'

                valid_item_values = {}
                if len(items_values) > 0:
                    for item_tag in items_values.keys():
                        if self._check_item_exist(group_name, item_tag) is True:
                            valid_item_values[item_tag] = items_values[item_tag]

                #
                item_tags_values = self._split_to_list(valid_item_values, size)
                for item_tags_value in item_tags_values:
                    results.update(self._write(group_name, item_tags_value, action))
                    time.sleep(interval)
            else:
                raise Exception(f"not connected")
            return results

        def properties(self, tags: list, ids=None):
            self._update_info(used=time.time())
            return list(self._properties(tags, ids))

        def list_items(self, paths: str = '*', recursive: bool = False, flat: bool = False, include_type: bool = False):
            self._update_info(used=time.time())
            return list(self._list_items(paths, recursive, flat, include_type))

        def servers(self, opc_host='localhost'):
            self._update_info(used=time.time())
            try:
                servers = self.opc_client.GetOPCServers(opc_host)
                servers = [s for s in servers if s is not None]
                return servers
            except pythoncom.com_error as err:
                raise Exception(f"servers: {self._get_error(err)}")

        def info(self):
            self._update_info(used=time.time())

            try:
                info_list = []
                mode = 'OpenOPC' if self.opc_svc else 'DCOM'

                info_list.append(('Protocol', mode))

                if mode == 'OpenOPC':
                    info_list.append(('',))
                    info_list.append(('Gateway Host', f"{self.opc_svc_host}:{self.opc_svc_port}"))
                    info_list.append(('Gateway Version', '1.4.0'))

                info_list.append(('Class', self.opc_class))
                info_list.append(('Client Name', self.opc_client.ClientName))
                info_list.append(('OPC Host', self.opc_svc_host))
                info_list.append(('OPC Server', self.opc_client.ServerName))
                info_list.append(('State', self.opc_status[self.opc_client.ServerState]))
                info_list.append(('Version', f"{self.opc_client.MajorVersion}.{self.opc_client.MinorVersion} (Build {self.opc_client.BuildNumber})"))

                try:
                    browser = self.opc_client.CreateBrowser()
                    browser_type = self.browser_types[browser.Organization]
                except:
                    browser_type = 'Not Supported'

                info_list.append(('Browser', browser_type))
                info_list.append(('Start Time', str(self.opc_client.StartTime)))
                info_list.append(('Current Time', str(self.opc_client.CurrentTime)))
                info_list.append(('Vendor', self.opc_client.VendorInfo))
                return info_list
            except pythoncom.com_error as err:
                raise Exception(f"info: {self._get_error(err)}")

        def ping(self):
            self._update_info(used=time.time())
            try:
                if self.opc_connected is True:
                    opc_serv_time = self.opc_client.CurrentTime
                    if opc_serv_time == self.opc_prev_serv_time:
                        return False
                    else:
                        self.opc_prev_serv_time = opc_serv_time
                        return True
            except pythoncom.com_error:
                pass
            return False

        def get_items(self):
            item_values = {}
            for client_handle, item in self.opc_client_handle_value.items():
                item_values[item.get('tag')] = item.get('value')
            return item_values

        ##########################
        def reset(self):
            self.opc_groups = {}
            self.opc_group_transaction_id = {}  # 订阅ID对应组号
            self.opc_client_handle = 0
            self.opc_client_handle_value = {}  # handle: value

        def _update_handle_value(self, client_handle: int, **kwargs):
            if client_handle not in self.opc_client_handle_value.keys():
                self.opc_client_handle_value[client_handle] = {}
            self.opc_client_handle_value[client_handle].update(**kwargs)

        def _exceptional(self, func, alt_return=None, alt_exceptions=(Exception,), final=None, catch=None):
            def __exceptional(*args, **kwargs):
                try:
                    try:
                        return func(*args, **kwargs)
                    except alt_exceptions:
                        return alt_return
                    except:
                        if catch: return catch(sys.exc_info(), lambda: func(*args, **kwargs))
                        raise
                finally:
                    if final: final()

            return __exceptional

        def _wild2regex(self, content: str):
            return content.replace('.', '\.').replace('*', '.*').replace('?', '.').replace('!', '^')

        def _type_check(self, tags: Union[list, tuple, str, None]):
            if isinstance(tags, list) or isinstance(tags, tuple):
                single = False
            elif tags is None:
                tags = []
                single = False
            else:
                tags = [tags]
                single = True

            if len([t for t in tags if type(t) not in (str, bytes)]) == 0:
                valid = True
            else:
                valid = False
            return tags, single, valid

        def _quality_str(self, quality_bits):
            quality = (quality_bits >> 6) & 3
            return self.opc_qualitys[quality]

        def _get_client(self):
            if self.opc_client is None:
                opc_client = None
                opc_classs = self.opc_class.split(';')
                for i, opc_class in enumerate(opc_classs):
                    try:
                        opc_client = win32com.client.gencache.EnsureDispatch(opc_class, 0)
                        server_event = win32com.client.WithEvents(opc_client, self.ServerEvents)
                        server_event.set_client(self)
                        self.opc_class = opc_class
                        break
                    except pythoncom.com_error as err:
                        if i == len(opc_classs) - 1:
                            raise Exception(f"get client fail(EnsureDispatch '{opc_class}' fail: {self._get_error(err)})")
                self.opc_client = opc_client
            return self.opc_client

        def _get_error(self, err) -> str:
            hr, msg, exc, arg = err.args

            if exc is None:
                error_str = str(msg)
            else:
                scode = exc[5]
                try:
                    opc_err_str = str(self.opc_client.GetErrorString(scode)).strip('\r\n')
                except:
                    opc_err_str = None

                try:
                    com_err_str = str(pythoncom.GetScodeString(scode)).strip('\r\n')
                except:
                    com_err_str = None

                if opc_err_str is None and com_err_str is None:
                    error_str = str(scode)
                elif opc_err_str == com_err_str:
                    error_str = opc_err_str
                elif opc_err_str is None:
                    error_str = com_err_str
                elif com_err_str is None:
                    error_str = opc_err_str
                else:
                    error_str = f'{opc_err_str} ({com_err_str})'
            return error_str

        def _update_info(self, **kwargs):
            self.opc_info.update(kwargs)

        def _remove_groups(self, groups: list, connect_status: bool = True):
            for group in groups:
                opc_group = self.opc_groups.get(group)
                if isinstance(opc_group, dict):
                    # 删除组
                    if connect_status is True:
                        self.remove_group(group)

                    group_event = opc_group.get('group_event')
                    if group_event is not None:
                        group_event.close()

                    opc_group = {}
                    del self.opc_groups[group]

        def _check_items(self, group_name: str, item_tags: list) -> list:
            opc_group = self.opc_groups.get(group_name, {}).get('group')
            if opc_group is not None:
                opc_items = opc_group.OPCItems
                item_tags.insert(0, 0)
                errors = []
                try:
                    errors = opc_items.Validate(len(item_tags) - 1, item_tags)
                except pythoncom.com_error as err:
                    raise Exception(f"valid group({group_name}) items fail({self._get_error(err)})")
                return errors
            raise Exception(f"valid group({group_name}) items fail")

        def _add_items(self, group_name: str, client_handles: list, valid_tags: list):
            opc_group = self.opc_groups.get(group_name, {}).get('group')
            if opc_group is not None:
                opc_items = opc_group.OPCItems
                try:
                    client_handles.insert(0, 0)
                    valid_tags.insert(0, 0)
                    return opc_items.AddItems(len(client_handles) - 1, valid_tags, client_handles)
                except Exception as e:
                    logging.error(f"add group({group_name}) items fail({e.__str__()})")
            return [], []

        def _check_item_exist(self, group_name: str, item_tag: str):
            tags = self.opc_groups.get(group_name, {}).get('tags', {})
            if item_tag in tags.keys():
                return True
            return False

        def _remove_items(self, group_name: str, server_handles: list):
            opc_group = self.opc_groups.get(group_name, {}).get('group')
            if opc_group is not None:
                opc_items = opc_group.OPCItems
                try:
                    return opc_items.AddItems(len(server_handles) - 1, server_handles)
                except pythoncom.com_error as err:
                    raise Exception(f"remove group({group_name}) items fail({self._get_error(err)})")

        def _update_values(self, client_handle: int, value, qualitie, timestamp, error, now_str):
            self._update_handle_value(client_handle, value=[value if type(value) != pywintypes.TimeType else str(value), self._quality_str(qualitie), str(timestamp), error, now_str])

        def _parse_value(self, group_name: str, item_tags: list, values: list, errors: list, qualities: list, timestamps: list) -> int:
            success = 0
            opc_group_tags = self.opc_groups.get(group_name, {}).get('tags', {})
            now_str = self.get_datetime_str()
            for i, item_tag in enumerate(item_tags):
                if item_tag in opc_group_tags.keys():
                    client_handle = opc_group_tags[item_tag]
                    if errors[i] == 0:
                        success = success + 1
                    self._update_values(client_handle, values[i], qualities[i], timestamps[i], self.opc_client.GetErrorString(errors[i]) if errors[i] != 0 else '', now_str)
            return success

        def _read(self, group_name: str, item_tags: Optional[list] = None, action: str = '', source: str = 'cache') -> dict:
            results = {}
            opc_group = self.opc_groups.get(group_name)
            if isinstance(opc_group, dict):

                opc_group_server_handles = opc_group.get('tags_handles', {})
                item_tags = [] if item_tags is None else item_tags
                if action == '':  # 订阅变化数据
                    pass
                elif action in ['sync', 'async']:  # sync同步读取
                    data_source = self.data_source.get(source, 1)
                    server_handles = {}
                    for item_tag in item_tags:
                        if item_tag in opc_group_server_handles.keys():
                            server_handles[item_tag] = opc_group_server_handles[item_tag]

                    if len(server_handles) > 0:
                        if action == 'sync':
                            self.sync_read(group_name, data_source, server_handles)
                        elif action == 'async':
                            self.async_read(group_name, server_handles)

                elif action == 'refresh':  # async异步读取
                    data_source = self.data_source.get(source, 1)
                    self.async_refresh(group_name, data_source)

                # 返回值
                opc_group_tags = opc_group.get('tags', {})
                for item_tag in item_tags:
                    if item_tag in opc_group_tags.keys():
                        client_handle = opc_group_tags[item_tag]
                        self._update_handle_value(client_handle, tag=item_tag)

                        if client_handle in self.opc_client_handle_value.keys():
                            results[item_tag] = self.opc_client_handle_value[client_handle].get('value')
            return results

        def _split_to_list(self, values, size: int):
            if isinstance(values, dict):
                results = [{}]
                for k, v in values.items():
                    if len(results[-1]) >= size:
                        results.append({k: v})
                    else:
                        results[-1][k] = v
                return results
            elif isinstance(values, list):
                return [values[i:i + size] for i in range(0, len(values), size)]
            return values

        def _write(self, group_name: str, items_values: dict, action: str = 'sync'):
            results = {}
            opc_group = self.opc_groups.get(group_name)
            if isinstance(opc_group, dict):
                opc_group_server_handles = opc_group.get('tags_handles', {})

                if action in ['sync', 'async']:  # sync同步读取
                    server_handles = []
                    item_tags = []
                    values = []
                    for item_tag in items_values.keys():
                        if item_tag in opc_group_server_handles.keys():
                            item_tags.append(item_tag)
                            server_handles.append(opc_group_server_handles[item_tag])
                            values.append(items_values[item_tag])

                    if len(server_handles) > 0:
                        if action == 'sync':
                            results.update(self.sync_write(group_name, server_handles.copy(), values.copy(), item_tags.copy()))
                        elif action == 'async':
                            results.update(self.async_write(group_name, server_handles.copy(), values.copy(), item_tags.copy()))
            return results

        def _properties(self, tags: list, id=None):
            try:
                tags, single_tag, valid = self._type_check(tags)
                if not valid:
                    raise Exception(f"tags must be a string or a list of strings")

                try:
                    id.remove(0)
                    include_name = True
                except:
                    include_name = False

                if id is not None:
                    descriptions = []

                    if isinstance(id, list) or isinstance(id, tuple):
                        property_id = list(id)
                        single_property = False
                    else:
                        property_id = [id]
                        single_property = True

                    for i in property_id:
                        descriptions.append('Property id %d' % i)
                else:
                    single_property = False

                for tag in tags:
                    if id is None:
                        count, property_id, descriptions, datatypes = self.opc_client.QueryAvailableProperties(tag)
                        tag_properties = list(map(lambda x, y: (x, y), property_id, descriptions))
                        property_id = [p for p, d in tag_properties if p > 0]
                        descriptions = [d for p, d in tag_properties if p > 0]

                    property_id.insert(0, 0)
                    values, errors = self.opc_client.GetItemProperties(tag, len(property_id) - 1, property_id)

                    property_id.pop(0)
                    values = [str(v) if type(v) == pywintypes.TimeType else v for v in values]

                    # Replace variant id with type strings
                    try:
                        i = property_id.index(1)
                        values[i] = vt[values[i]]
                    except:
                        pass

                    # Replace quality bits with quality strings
                    try:
                        i = property_id.index(3)
                        values[i] = self._quality_str(values[i])
                    except:
                        pass

                    # Replace access rights bits with strings
                    try:
                        i = property_id.index(5)
                        values[i] = self.access_rights[values[i]]
                    except:
                        pass

                    if id != None:
                        if single_property:
                            if single_tag:
                                tag_properties = values
                            else:
                                tag_properties = [values]
                        else:
                            tag_properties = list(map(lambda x, y: (x, y), property_id, values))
                    else:
                        tag_properties = list(map(lambda x, y, z: (x, y, z), property_id, descriptions, values))
                        tag_properties.insert(0, (0, 'Item ID (virtual property)', tag))

                    if include_name:    tag_properties.insert(0, (0, tag))
                    if not single_tag:  tag_properties = [tuple([tag] + list(p)) for p in tag_properties]

                    for p in tag_properties: yield p

            except pythoncom.com_error as err:
                raise Exception(f"properties fail({self._get_error(err)})")

        def _list_items(self, paths: str = '*', recursive: bool = False, flat: bool = False, include_type: bool = False):
            try:
                try:
                    browser = self.opc_client.CreateBrowser()
                except:
                    return

                paths, single, valid = self._type_check(paths)
                if not valid:
                    raise TypeError("paths must be a string or a list of strings")
                if len(paths) == 0:
                    paths = ['*']
                nodes = {}
                for path in paths:
                    if flat:
                        browser.MoveToRoot()
                        browser.Filter = ''
                        browser.ShowLeafs(True)
                        pattern = re.compile('^%s$' % self._wild2regex(path), re.IGNORECASE)
                        matches = filter(pattern.search, browser)
                        if include_type:  matches = [(x, node_type) for x in matches]
                        for node in matches: yield node
                        continue

                    queue = []
                    queue.append(path)

                    while len(queue) > 0:
                        tag = queue.pop(0)

                        browser.MoveToRoot()
                        browser.Filter = ''
                        pattern = None

                        path_str = '/'
                        path_list = tag.replace('.', '/').split('/')
                        path_list = [p for p in path_list if len(p) > 0]
                        found_filter = False
                        path_postfix = '/'

                        for i, p in enumerate(path_list):
                            if found_filter:
                                path_postfix += p + '/'
                            elif p.find('*') >= 0:
                                pattern = re.compile('^%s$' % self._wild2regex(p), re.IGNORECASE)
                                found_filter = True
                            elif len(p) != 0:
                                pattern = re.compile('^.*$')
                                browser.ShowBranches()

                                # Branch node, so move down
                                if len(browser) > 0:
                                    try:
                                        browser.MoveDown(p)
                                        path_str += p + '/'
                                    except:
                                        if i < len(path_list) - 1: return
                                        pattern = re.compile('^%s$' % self._wild2regex(p), re.IGNORECASE)

                                else:
                                    p = '.'.join(path_list[i:])
                                    pattern = re.compile('^%s$' % self._wild2regex(p), re.IGNORECASE)
                                    break

                        browser.ShowBranches()

                        if len(browser) == 0:
                            browser.ShowLeafs(False)
                            lowest_level = True
                            node_type = 'Leaf'
                        else:
                            lowest_level = False
                            node_type = 'Branch'

                        matches = filter(pattern.search, browser)

                        if not lowest_level and recursive:
                            queue += [path_str + x + path_postfix for x in matches]
                        else:
                            if lowest_level:  matches = [self._exceptional(browser.GetItemID, x)(x) for x in matches]
                            if include_type:  matches = [(x, node_type) for x in matches]
                            for node in matches:
                                if not node in nodes: yield node
                                nodes[node] = True
            except pythoncom.com_error as err:
                raise Exception(f"list item fail({self._get_error(err)})")

        def _update_group_info(self, name: str, **kwargs):
            if name not in self.opc_groups.keys():
                self.opc_groups[name] = {'name': name}
            self.opc_groups[name].update(**kwargs)

        def _get_group_info(self, name: str, key: str, defaul):
            return self.opc_groups.get(name, {}).get(key, defaul)

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        self.host = 'localhost' if host is None else host
        self.port = 8810 if host is None else port

    def get_sessions(self):
        return Pyro4.Proxy(f"PYRO:opc@{self.host}:{self.port}").get_clients()

    def close_session(self, guid):
        return Pyro4.Proxy(f"PYRO:opc@{self.host}:{self.port}").force_close(guid)

    def close_all_sessions(self):
        return Pyro4.Proxy(f"PYRO:opc@{self.host}:{self.port}").close_all_sessions()

    def open_client(self):
        return Pyro4.Proxy(f"PYRO:opc@{self.host}:{self.port}").create_client()

    def get_info(self):
        return Pyro4.Proxy(f"PYRO:opc@{self.host}:{self.port}").get_info()

    def restart(self):
        return Pyro4.Proxy(f"PYRO:opc@{self.host}:{self.port}").restart()


class IOTOPCDA(IOTDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reinit()

    def reinit(self):
        self.exit_flag = False
        IOTBaseCommon.function_thread(self.pump_wait_msg, False).start()

    def exit(self):
        self.exit_flag = True
        self.close()
        self.reinit()

    @classmethod
    def template(cls, mode: int, type: str, lan: str) -> List[Dict[str, Any]]:
        templates = []
        if type == 'point':
            templates.extend([
                {'required': True, 'name': '是否可写' if lan == 'ch' else 'writable'.upper(), 'code': 'point_writable', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                {'required': True, 'name': '物理点名' if lan == 'ch' else 'name'.upper(), 'code': 'point_name', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''},
                {'required': True, 'name': 'OPC标签' if lan == 'ch' else 'tag'.upper(), 'code': 'point_tag', 'type': 'string', 'default': 'Bucket Brigade.Int2', 'enum': [], 'tip': ''},
                {'required': False, 'name': 'OPC标签类型' if lan == 'ch' else 'type'.upper(), 'code': 'point_type', 'type': 'string', 'default': 'VT_R4', 'enum': [], 'tip': ''},
                {'required': False, 'name': 'OPC标签描述' if lan == 'ch' else 'description'.upper(), 'code': 'point_description', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''},
                {'required': False, 'name': '逻辑点名' if lan == 'ch' else 'name alias'.upper(), 'code': 'point_name_alias', 'type': 'string', 'default': 'Chiller_1_CHW_ENT1', 'enum': [], 'tip': ''},
                {'required': True, 'name': '是否启用' if lan == 'ch' else 'enable'.upper(), 'code': 'point_enabled', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                {'required': True, 'name': '倍率' if lan == 'ch' else 'scale'.upper(), 'code': 'point_scale', 'type': 'string', 'default': '1', 'enum': [], 'tip': ''}
                ])

        elif type == 'config':
            templates.extend([
                {'required': True, 'name': 'OPC服务名称' if lan == 'ch' else 'Server Name', 'code': 'server', 'type': 'string', 'default': 'Matrikon.OPC.Simulation.1', 'enum': [], 'tip': ''},
                {'required': True, 'name': 'OPC服务地址' if lan == 'ch' else 'Host', 'code': 'host', 'type': 'string', 'default': 'localhost:7766', 'enum': [], 'tip': ''},
                {'required': False, 'name': '读取方式' if lan == 'ch' else 'Action', 'code': 'action', 'type': 'string', 'default': 'sync', 'enum': ['', 'sync', 'async'], 'tip': ''},
                {'required': True, 'name': 'OPC组名' if lan == 'ch' else 'Group', 'code': 'group', 'type': 'string', 'default': 'opc1', 'enum': [], 'tip': ''},
                {'required': True, 'name': 'OPC最大点位限制' if lan == 'ch' else 'Limit', 'code': 'limit', 'type': 'int', 'default': 10000, 'enum': [], 'tip': ''},
                {'required': True, 'name': '单次读取限制' if lan == 'ch' else 'Read Limit', 'code': 'read_limit', 'type': 'int', 'default': 1000, 'enum': [], 'tip': ''},
                {'required': True, 'name': '更新速率(ms)' if lan == 'ch' else 'Update Rate(ms)', 'code': 'update_rate', 'type': 'int', 'default': 500, 'enum': [], 'tip': ''}
            ])
        return templates
    
    ###API#############
    def read(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        results = {}
        names = kwargs.get('names', list(self.points.keys()))
        read_items = []
        for name in names:
            point = self.points.get(name)
            if point:
                tag = point.get('point_tag')
                if tag is not None and tag not in read_items:
                    read_items.append(tag)

        datas = self._read(read_items)

        for name in names:
            point = self.points.get(name)
            if point:
                tag = point.get('point_tag')
                value = self._get_value(datas, name, tag)
                if value is not None:
                    results[name] = value

        self.update_info(read=len(names), response=len(results))
        return results

    def write(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())

        results = {}
        write_items = {}
        values = kwargs.get('values', {})
        for name, value in values.items():
            point = self.points.get(name)
            if point:
                tag = point.get('point_tag')
                if tag is not None:
                    write_items[tag] = value
            else:
                results[name] = [False, 'UnExist']

        datas = self._write(write_items)

        for name, value in values.items():
            point = self.points.get(name)
            if point:
                tag = point.get('point_tag')
                if tag in datas.keys():
                    results[name] = datas[tag]
                    if results[name][0] is False:
                        logging.error(f"set item({name}) fail({results[name][1]})")
        return results

    def ping(self, **kwargs) -> bool:
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        return self._get_client() and self._get_client().ping()

    def scan(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        results = {}
        if self._get_client():
            path = kwargs.get('path', '*')
            include_property = kwargs.get('include_property', False)
            self.logging(content=f"scan opc({path})")
            points = self._get_client().list_items(paths=path, flat=True)  # flat=True
            self.logging(content=f"scan opc flags({len(points)})")
            for point in points:
                params = {'point_name': point, 'point_name_alias': point, 'point_writable': True, 'point_tag': point, 'point_type': '', 'point_description': '', 'point_value': ''}
                if include_property is True:
                    properties = self._get_client().properties(tags=[point])
                    self.logging(content=f"scan opc item({point}) property({len(properties)})")
                    for property in properties:
                        if len(property) >= 3:
                            if property[2] == 'Item Canonical DataType':
                                params['point_type'] = str(property[3])
                            elif property[2] == 'Item Value':
                                params['point_value'] = str(property[3])
                            elif property[2] == 'Item Description':
                                params['point_description'] = property[3]
                results[point] = self.create_point(**params)
        self.update_info(scan=len(results))
        return results

    def discover(self, **kwargs):
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        results = []
        if self._get_client(False):
            results = self._get_client(False).servers(opc_host=self.configs.get('host', 'localhost'))
        self.update_info(discover=len(results))
        return results

    ###################

    def _get_host_info(self) -> Optional[dict]:
        host = self.configs.get('host')
        if len(host) > 0:
            host_info = host.split(':')
            if len(host_info) == 1:
                return {'com': True, 'ip': host_info[0], 'port': None, 'server': self.configs.get('server'), 'group': self.configs.get('group')}
            elif len(host_info) == 2:
                return {'com': False, 'ip': host_info[0], 'port': int(float(host_info[1])), 'server': self.configs.get('server'), 'group': self.configs.get('group')}
        return None

    def _release_client(self, client):
        try:
            if client:
                client.close()
        except Exception as e:
            print(f'release client fail({e.__str__()})')
        finally:
            client = None

    def _get_client(self, auto_connect: bool = True):
        if self.client is None:
            info = self._get_host_info()
            if isinstance(info, dict):
                client = None
                try:
                    if info.get('com') is True:
                        client = OPCDA.OPCClient()
                    else:
                        client = OPCDA(info.get('ip'), info.get('port')).open_client()

                    if auto_connect is True:
                        client.connect(info.get('server'), info.get('host'))
                        self.logging(content=f"connect opc({info.get('host')}-{info.get('server')})")

                    client.add_group(self.configs.get('group'), self.configs.get('update_rate'))
                    self.logging(content=f"add opc group({self.configs.get('group')})")
                except Exception as e:
                    self._release_client(client)
                    raise e
                self.client = client
        return self.client

    def pump_wait_msg(self):
        while self.exit_flag is False:
            try:
                if self.client is not None and self.client.is_connected() is True:
                    pythoncom.PumpWaitingMessages()
                    continue
            except:
                pass
            time.sleep(0.1)

    def _read(self, tags: list):
        results = {}
        if len(tags) > 0 and self._get_client():
            chunk_tags = IOTBaseCommon.chunk_list(tags, self.configs.get('read_limit', 100))
            for chunk_tag in chunk_tags:
                values = self._get_client().read(self.configs.get('group'), chunk_tag, self.configs.get('action'))
                for tag, value in values.items():
                    if isinstance(value, list):
                        if len(value) >= 4:
                            (v, status, time, error, update) = value
                            if status == 'Good':
                                results[tag] = [True, v]
                            else:
                                results[tag] = [False, f"[{status}] {error}"]
                    else:
                        results[tag] = [False, str(value)]
        return results

    def _get_value(self, results: dict, name: str, tag: str):
        if tag in results.keys():
            [flag, value] = results[tag]
            if flag is True:
                return value
            else:
                logging.error(f"get item({name}) fail({value})")
        return None

    def _write(self, set_values: dict) -> dict:
        if len(set_values) > 0 and self._get_client():
            return self._get_client().write(self.configs.get('group'), set_values)
        return {}

    def close(self):
        if self.client is not None:
            self._release_client(self.client)
        self.client = None

    def info(self, **kwargs):
        if self._get_client():
            return self._get_client().get_info()