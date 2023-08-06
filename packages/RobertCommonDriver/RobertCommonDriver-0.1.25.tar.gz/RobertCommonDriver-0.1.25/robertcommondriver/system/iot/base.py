import logging
import os
import platform
import psutil
import re
import requests
import socket
import time
import uuid

from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from decimal import Decimal
from enum import Enum
from functools import wraps
from func_timeout import func_timeout
from func_timeout.exceptions import FunctionTimedOut
from ipaddress import ip_network, ip_address
from multiprocessing import Pool
from queue import Queue
from requests.auth import AuthBase
from struct import pack, unpack
from threading import Timer, Thread
from typing import Callable, Union, Optional, Any, TypeVar, NamedTuple, List

JsonType = TypeVar('JsonType')


class IOTBaseCommon:

    class CloseException(Exception):
        pass

    class NormalException(Exception):
        pass

    class DataTransform:

        class DataFormat(Enum):
            '''应用于多字节数据的解析或是生成格式'''
            ABCD = 0        # 按照顺序排序   Modbus 十进制数字123456789或十六进制07 5B CD 15 07 5B CD 15
            BADC = 1        # 按照单字反转
            CDAB = 2        # 按照双字反转 (大部分PLC默认排序方法)
            DCBA = 3        # 按照倒序排序

        class TypeFormat(Enum):
            BOOL = 0
            BOOL_ARRAY = 1
            INT8 = 2
            INT8_ARRAY = 3
            UINT8 = 4
            UINT8_ARRAY = 5
            INT16 = 6
            INT16_ARRAY = 7
            UINT16 = 8
            UINT16_ARRAY = 9
            INT32 = 10
            INT32_ARRAY = 11
            UINT32 = 12
            UINT32_ARRAY = 13
            INT64 = 14
            INT64_ARRAY = 15
            UINT64 = 16
            UINT64_ARRAY = 17
            FLOAT = 18
            FLOAT_ARRAY = 19
            DOUBLE = 20
            DOUBLE_ARRAY = 21
            STRING = 22
            HEX_STRING = 23

        @staticmethod
        def get_type_word_size(type: int, length: int = 0):
            if type in [IOTBaseCommon.DataTransform.TypeFormat.BOOL, IOTBaseCommon.DataTransform.TypeFormat.BOOL_ARRAY, IOTBaseCommon.DataTransform.TypeFormat.INT8, IOTBaseCommon.DataTransform.TypeFormat.UINT8, IOTBaseCommon.DataTransform.TypeFormat.INT16, IOTBaseCommon.DataTransform.TypeFormat.UINT16]:
                return 1
            elif type in [IOTBaseCommon.DataTransform.TypeFormat.INT32, IOTBaseCommon.DataTransform.TypeFormat.UINT32, IOTBaseCommon.DataTransform.TypeFormat.FLOAT]:
                return 2
            elif type in [IOTBaseCommon.DataTransform.TypeFormat.INT64, IOTBaseCommon.DataTransform.TypeFormat.UINT64, IOTBaseCommon.DataTransform.TypeFormat.DOUBLE]:
                return 4
            return length

        @staticmethod
        def int_or_none(i: Union[None, int, str, float]) -> Optional[int]:
            return None if i is None else int(float(i))

        @staticmethod
        def float_or_none(f: Union[None, int, str, float]) -> Optional[float]:
            return None if f is None else float(f)

        # 将字节数组转换成十六进制的表示形式
        @staticmethod
        def bytes_to_hex_string(bytes: bytearray, segment: str = ' '):
            return segment.join(['{:02X}'.format(byte) for byte in bytes])

        # 从字节数组中提取bool数组变量信息
        @staticmethod
        def bytes_to_bool_array(bytes: bytearray, length: int = None):
            if bytes is None:
                return None
            if length is None or length > len(bytes) * 8:
                length = len(bytes) * 8

            buffer = []
            for i in range(length):
                index = i // 8
                offect = i % 8
                temp_array = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]
                temp = temp_array[offect]
                if (bytes[index] & temp) == temp:
                    buffer.append(True)
                else:
                    buffer.append(False)
            return buffer

        # 将buffer中的字节转化成byte数组对象
        @staticmethod
        def trans_byte_array(bytes: bytearray, index: int, length: int):
            data = bytearray(length)
            for i in range(length):
                data[i] = bytes[i + index]
            return data

        # 将buffer数组转化成bool数组对象，需要转入索引，长度
        @staticmethod
        def trans_byte_bool_array(bytes: bytearray, index: int, length: int):
            data = bytearray(length)
            for i in range(length):
                data[i] = bytes[i + index]
            return IOTBaseCommon.DataTransform.bytes_to_bool_array(data)

        # 将buffer中的字节转化成byte对象
        @staticmethod
        def trans_byte(bytes: bytearray, index: int):
            return bytes[index]

        # 反转多字节
        @staticmethod
        def reverse_bytes(bytes: bytearray, length: int, index: int = 0, format: DataFormat = DataFormat.ABCD):
            buffer = bytearray(length)
            if format == IOTBaseCommon.DataTransform.DataFormat.ABCD:
                for i in range(length):
                    buffer[i] = bytes[index + i]
            elif format == IOTBaseCommon.DataTransform.DataFormat.BADC:
                for i in range(int(length / 2)):
                    buffer[2 * i] = bytes[index + 2 * i + 1]
                    buffer[2 * i + 1] = bytes[index + 2 * i]
            elif format == IOTBaseCommon.DataTransform.DataFormat.CDAB:
                for i in range(int(length / 2)):
                    buffer[2 * i] = bytes[index + length - 2 * (i + 1)]
                    buffer[2 * i + 1] = bytes[index + length - 2 * (i + 1) + 1]
            elif format == IOTBaseCommon.DataTransform.DataFormat.DCBA:
                for i in range(length):
                    buffer[i] = bytes[index + length - i - 1]
            return buffer

        @staticmethod
        def get_type_size_fmt(type: TypeFormat, little_indian: bool = True):
            type_size = 1
            type_fmt = '<h' if little_indian else '>h'
            if type in [IOTBaseCommon.DataTransform.TypeFormat.INT8, IOTBaseCommon.DataTransform.TypeFormat.INT8_ARRAY]:
                type_size = 1
                type_fmt = '<b' if little_indian else '>b'
            elif type in [IOTBaseCommon.DataTransform.TypeFormat.UINT8, IOTBaseCommon.DataTransform.TypeFormat.UINT8_ARRAY]:
                type_size = 1
                type_fmt = '<B' if little_indian else '>B'
            elif type in [IOTBaseCommon.DataTransform.TypeFormat.INT16, IOTBaseCommon.DataTransform.TypeFormat.INT16_ARRAY]:
                type_size = 2
                type_fmt = '<h' if little_indian else '>h'
            elif type in [IOTBaseCommon.DataTransform.TypeFormat.UINT16, IOTBaseCommon.DataTransform.TypeFormat.UINT16_ARRAY]:
                type_size = 2
                type_fmt = '<H' if little_indian else '>H'
            elif type in [IOTBaseCommon.DataTransform.TypeFormat.INT32, IOTBaseCommon.DataTransform.TypeFormat.INT32_ARRAY]:
                type_size = 4
                type_fmt = '<i' if little_indian else '>i'
            elif type in [IOTBaseCommon.DataTransform.TypeFormat.UINT32, IOTBaseCommon.DataTransform.TypeFormat.UINT32_ARRAY]:
                type_size = 4
                type_fmt = '<I' if little_indian else '>I'
            elif type in [IOTBaseCommon.DataTransform.TypeFormat.INT64, IOTBaseCommon.DataTransform.TypeFormat.INT64_ARRAY]:
                type_size = 8
                type_fmt = '<q' if little_indian else '>q'
            elif type in [IOTBaseCommon.DataTransform.TypeFormat.UINT64, IOTBaseCommon.DataTransform.TypeFormat.UINT64_ARRAY]:
                type_size = 8
                type_fmt = '<Q' if little_indian else '>Q'
            elif type in [IOTBaseCommon.DataTransform.TypeFormat.FLOAT, IOTBaseCommon.DataTransform.TypeFormat.FLOAT_ARRAY]:
                type_size = 4
                type_fmt = '<f' if little_indian else '>f'
            elif type in [IOTBaseCommon.DataTransform.TypeFormat.DOUBLE, IOTBaseCommon.DataTransform.TypeFormat.DOUBLE_ARRAY]:
                type_size = 8
                type_fmt = '<d' if little_indian else '>d'
            return type_size, type_fmt

        # 将bytes转换成各种值
        @staticmethod
        def convert_bytes_to_values(bytes: bytearray, type: TypeFormat, index: int, length: int = 1, encoding: str = '', little_endian: bool = True) -> list:

            if type == IOTBaseCommon.DataTransform.TypeFormat.STRING:
                return [IOTBaseCommon.DataTransform.trans_byte_array(bytes, index, length).decode(encoding)]
            elif type == IOTBaseCommon.DataTransform.TypeFormat.HEX_STRING:
                return [IOTBaseCommon.DataTransform.bytes_to_hex_string(bytes)]
            elif type in [IOTBaseCommon.DataTransform.TypeFormat.BOOL, IOTBaseCommon.DataTransform.TypeFormat.BOOL_ARRAY]:
                return IOTBaseCommon.DataTransform.trans_byte_bool_array(bytes, index, len(bytes))

            type_size, type_fmt = IOTBaseCommon.DataTransform.get_type_size_fmt(type, little_endian)
            return [unpack(type_fmt, IOTBaseCommon.DataTransform.trans_byte_array(bytes, index + type_size * i, type_size))[0] for i in range(length)]

        # 从bool数组变量变成byte数组
        @staticmethod
        def convert_bool_array_to_byte(values: list):
            if (values == None): return None

            length = 0
            if len(values) % 8 == 0:
                length = int(len(values) / 8)
            else:
                length = int(len(values) / 8) + 1
            buffer = bytearray(length)
            for i in range(len(values)):
                index = i // 8
                offect = i % 8

                temp_array = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]
                temp = temp_array[offect]

                if values[i]: buffer[index] += temp
            return buffer

        # 将各种类型值转换为bytes
        @staticmethod
        def convert_values_to_bytes(values: Any, type: TypeFormat, encoding: str = '', little_endian: bool = True):
            if values is None:
                return None

            buffer = None
            if type == IOTBaseCommon.DataTransform.TypeFormat.STRING:
                buffer = values.encode(encoding)
            elif type == IOTBaseCommon.DataTransform.TypeFormat.HEX_STRING:
                buffer = bytes.fromhex(values)
            else:
                if not isinstance(values, list):
                    values = [values]
                if type in [IOTBaseCommon.DataTransform.TypeFormat.BOOL, IOTBaseCommon.DataTransform.TypeFormat.BOOL_ARRAY]:
                    buffer = IOTBaseCommon.DataTransform.convert_bool_array_to_byte(values)
                else:
                    type_size, type_fmt = IOTBaseCommon.DataTransform.get_type_size_fmt(type, little_endian)
                    buffer = bytearray(len(values) * type_size)
                    for i in range(len(values)):
                        buffer[(i * type_size): (i + 1) * type_size] = pack(type_fmt, values[i])
            return buffer

        @staticmethod
        def format_bytes(data: bytes) -> str:
            return ''.join(["%02X" % x for x in data]).strip()

        @staticmethod
        def convert_value_to_values(value, src_type: TypeFormat, dst_type: TypeFormat, format: Optional[DataFormat] = DataFormat.ABCD, little_endian: bool = True):
            bytes = IOTBaseCommon.DataTransform.convert_values_to_bytes(value, src_type, little_endian=little_endian)  # CDAB
            bytes = IOTBaseCommon.DataTransform.reverse_bytes(bytes, len(bytes), 0, format)  # 转换为指定顺序
            type_size, type_fmt = IOTBaseCommon.DataTransform.get_type_size_fmt(dst_type, little_endian)
            return IOTBaseCommon.DataTransform.convert_bytes_to_values(bytes, dst_type, 0, int(len(bytes)/type_size), little_endian=little_endian)

        @staticmethod
        def convert_values_to_value(values: list, src_type: TypeFormat, dst_type: TypeFormat, format: Optional[DataFormat] = DataFormat.ABCD, pos: int = 0, little_endian: bool = True):
            if len(values) <= 0:
                return None
            bytes = IOTBaseCommon.DataTransform.convert_values_to_bytes(values, src_type, little_endian=little_endian)  # CDAB
            bytes = IOTBaseCommon.DataTransform.reverse_bytes(bytes, len(bytes), 0, format)  # 转换为指定顺序
            type_size, type_fmt = IOTBaseCommon.DataTransform.get_type_size_fmt(dst_type, little_endian)
            return IOTBaseCommon.DataTransform.convert_bytes_to_values(bytes, dst_type, 0, int(len(bytes)/type_size), little_endian=little_endian)[pos]

        @staticmethod
        def convert_value(values: Any, src_type: TypeFormat, dst_type: TypeFormat, format: Optional[DataFormat] = DataFormat.ABCD, pos: int = -1, little_endian: bool = True):
            bytes = IOTBaseCommon.DataTransform.convert_values_to_bytes(values, src_type, little_endian=little_endian)  # CDAB
            bytes = IOTBaseCommon.DataTransform.reverse_bytes(bytes, len(bytes), 0, format)  # 转换为指定顺序
            type_size, type_fmt = IOTBaseCommon.DataTransform.get_type_size_fmt(dst_type, little_endian)
            results = IOTBaseCommon.DataTransform.convert_bytes_to_values(bytes, dst_type, 0, int(len(bytes) / type_size), little_endian=little_endian)
            if pos >= 0 and pos < len(results):
                return results[pos]
            return results

        # 比较两个数组
        @staticmethod
        def compare_bytes(bytes1: bytearray, bytes2: bytearray, length: int, start1: int = 0, start2: int = 0):
            if bytes1 == None or bytes2 == None: return False
            for i in range(length):
                if bytes1[i + start1] != bytes2[i + start2]: return False
            return True

    class RepeatingTimer(Timer):

        def run(self):
            self.finished.wait(self.interval)
            while not self.finished.is_set():
                self.function(*self.args, **self.kwargs)
                self.finished.wait(self.interval)

    class SimpleTimer:

        def __init__(self):
            self.timer = None

        def is_running(self):
            return self.timer and self.timer.is_alive()

        def run(self, interval: int, function: Callable, args=None, kwargs=None):
            if self.is_running():
                if kwargs.get('force', False) is False:
                    raise Exception(f"timer is running, please cancel")
                else:
                    self.cancel()
            self._run_timer(interval, function, args, kwargs)

        def _run_timer(self, interval: int, function: Callable, args=None, kwargs=None):
            self.timer = Timer(interval, function, args, kwargs)
            self.timer.start()

        def cancel(self):
            if self.is_running():
                self.timer.cancel()
            self.timer = None

    class RepeatThreadPool:

        def __init__(self, size: int, fun: Optional[Callable] = None, done_callback: Optional[Callable] = None, **kwargs):
            self.kwargs = kwargs
            self.pool_size = size              # 线程池大小
            self.pool_fun = fun                # 线程函数
            self.pools = ThreadPoolExecutor(self.pool_size) # 线程池
            self.done_callback = done_callback              # 线程执行回调函数

            self.task_queue = Queue()               # 待处理队列
            self.task_cache = {}                    # 全部任务
            self.task_running = {}                  # 正在处理任务
            self.pool_status = 'running'
            self.task_finish: int = 0               # 已完成任务

        def __del__(self):
            self.pools.shutdown()
            self.pool_status = 'shutdown'

        def process_task(self):
            if self.task_queue.empty() is False and len(self.task_running) <= self.pool_size:
                task_index = self.task_queue.get()
                if isinstance(task_index, int) and task_index > 0:
                    task_info = self.task_cache.get(task_index)
                    if isinstance(task_info, dict):
                        task_info['process'] = time.time()
                        future = self.pools.submit(task_info.get('task'), *(task_info.get('args')))
                        self.task_running[future] = task_index
                        future.add_done_callback(self.future_callback)

        def add_task(self, task, task_back, *args, **kwargs) -> int:
            index = len(self.task_cache) + 1
            self.task_cache[index] = {'index': index, 'create': time.time(), 'task': task, 'task_back': task_back, 'args': args, 'kwargs': kwargs}
            self.task_queue.put(index)
            return index

        def submit_task(self, task: Optional[Callable], task_back: Optional[Callable], *args, **kwargs) -> int:
            if len(args) > 0:
                task = task if task else self.pool_fun
                task_back = task_back if task_back else self.done_callback
                task_index = self.add_task(task, task_back, *args, **kwargs)
                self.process_task()
                return task_index
            return 0

        def reactive_task(self, future):
            if future is not None and future in self.task_running.keys():
                del self.task_running[future]

            # 触发响应
            self.process_task()

        def future_callback(self, future):
            self.task_finish = self.task_finish + 1
            if future in self.task_running.keys():
                task_info = self.task_cache.get(self.task_running[future])
                if isinstance(task_info, dict):
                    task_info['future'] = future
                    task_info['result'] = future.result()
                    task_info['end'] = time.time()
                    task_info['cost'] = '{:.3f}'.format(task_info['end'] - task_info['process'])
                    done_callback = task_info.get('task_back')
                    if done_callback:
                        done_callback(task_info)

        def finish(self) -> bool:
            if self.task_queue.empty() is True and len(self.task_running) == 0:
                self.pool_status = 'finish'
                return True
            return False

        def done(self):
            while self.finish() is False:
                time.sleep(1)

        def status(self):
            return self.pool_status

        def info(self):
            return {'total': len(self.task_cache), 'running': len(self.task_running), 'finish': self.task_finish}

    class SimpleThreadPool:

        def __init__(self, size: int, fun: Optional[Callable] = None, done_callback: Optional[Callable] = None, **kwargs):
            self.kwargs = kwargs
            self.pool_size = size              # 线程池大小
            self.pool_fun = fun                # 线程函数
            self.pools = ThreadPoolExecutor(self.pool_size) # 线程池
            self.done_callback = done_callback              # 线程执行回调函数
            self.task_future = []

        def submit_task(self, task: Optional[Callable], *args, **kwargs):
            task = task if task else self.pool_fun
            if task is not None:
                self.task_future.append(self.pools.submit(task, *args, **kwargs))

        def done(self, dict_result: bool = True):
            results_dict = {}
            results_list = []
            for future in as_completed(self.task_future):
                result = future.result()
                if result is not None:
                    if isinstance(result, dict):
                        results_dict.update(result)
                    elif isinstance(result, list):
                        results_list.extend(result)
                    else:
                        results_list.append(result)
            return results_dict if dict_result else results_list

    class Response(NamedTuple):
        success: bool
        code: str
        msg: Optional[str]
        data: Optional[JsonType]
        headers: Optional[dict] = None

    class MultiPool:

        def __init__(self, pool_size: int, pool_fun: Callable, fun_params: list):
            self.pool_size = pool_size
            self.pool_fun = pool_fun
            self.fun_params = fun_params
            self.pool_cost = 0

        def run(self, dict_result: bool = True):
            start = time.time()
            results_dict = {}
            results_list = []
            with Pool(self.pool_size) as p:
                p.map(self.pool_fun, self.fun_params)

                for result in p.imap_unordered(self.pool_fun, self.fun_params):
                    if result is not None:
                        if isinstance(result, dict):
                            results_dict.update(result)
                        elif isinstance(result, list):
                            results_list.extend(result)
                        else:
                            results_list.append(result)

            self.pool_cost = '{:.3f}'.format(time.time() - start)
            return results_dict if dict_result else results_list

        def cost(self):
            return self.pool_cost

    class IECSocketClient():

        def __init__(self, host: str, port: int, timeout: float, callbacks: Optional[dict] = None):
            self.valid = True
            self.host = host
            self.port = port
            self.sock = None
            self.timeout = timeout
            self.callbacks = {} if callbacks is None else callbacks
            self.connect()
            IOTBaseCommon.function_thread(self.receive, True).start()
            self.handle_connect()

        def __str__(self):
            return f"{self.host}:{self.port}"

        def __del__(self):
            self.exit()

        def exit(self):
            self.valid = False
            self.close()

        def connect(self):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)  # 设置连接超时
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(None)

        def close(self):
            if self.sock:
                self.sock.close()

        def send(self, datas: bytes):
            # print(f"Send: {self.format_bytes(datas)}")
            if self.sock:
                self.sock.send(datas)

        def format_bytes(self, data: bytes) -> str:
            return ' '.join(["%02X" % x for x in data]).strip()

        def check_invalid(self) -> bool:
            return self.valid

        def recv_bytes(self, length: int) -> Optional[bytes]:
            data = b''
            while self.check_invalid() is True and len(data) < length:
                rec_length = length - len(data)
                rec_data = self.sock.recv(rec_length)
                if rec_data is None or len(rec_data) == 0:
                    raise IOTBaseCommon.CloseException(f"remote close")
                data += rec_data
            if len(data) != length:
                return None
            return data

        def receive(self):
            try:
                while self.valid is True:
                    start_bytes = self.recv_bytes(1)
                    if start_bytes == bytes.fromhex('68'):
                        length_bytes = self.recv_bytes(1)
                        length = length_bytes[0] # 包长
                        datas = self.recv_bytes(length)
                        # print(f"Recv: {self.format_bytes(start_bytes + length_bytes + datas)}")
                        if 'handle_data' in self.callbacks.keys():
                            self.callbacks['handle_data'](self, start_bytes + length_bytes + datas)
            except socket.timeout as e:
                pass
            except IOTBaseCommon.NormalException as e:
                logging.error(e.__str__())
            except IOTBaseCommon.CloseException as e:
                self.handle_close(e.__str__())
            except Exception as e:
                self.handle_error(e)

        def handle_error(self, e: Exception):
            if 'handle_error' in self.callbacks.keys():
                self.callbacks['handle_error'](self, e)
            self.close()
            self.valid = False

        def handle_close(self, reason: str=''):
            if 'handle_close' in self.callbacks.keys():
                self.callbacks['handle_close'](self, reason)
            self.close()
            self.valid = False

        def handle_connect(self):
            if 'handle_connect' in self.callbacks.keys():
                self.callbacks['handle_connect'](self)

    @staticmethod
    def function_thread(fn: Callable, daemon: bool, *args, **kwargs):
        return Thread(target=fn, args=args, kwargs=kwargs, daemon=daemon)

    @staticmethod
    def chunk_list(values: list, num: int):
        for i in range(0, len(values), num):
            yield values[i: i + num]

    @staticmethod
    def get_datetime() -> datetime:
        return datetime.now()

    @staticmethod
    def get_datetime_str() -> str:
        return IOTBaseCommon.get_datetime().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_networks(ip: str):
        ips = []
        m = re.compile(r"(\d+\.\d+\.\d+\.\d+)(?:/(\d+))?(?::(\d+))?").match(ip)
        if m:
            (_ip, net, port) = m.groups()
            __ip = f"{_ip}/{net}" if net is not None else f"{_ip}/24"
            ip_start = ip_address(str(ip_network(__ip, False)).split('/')[0])
            num_addresses = ip_network(__ip, False).num_addresses
            for i in range(num_addresses):
                ips.append(str(ip_address(ip_start) + i))
        return ips

    @staticmethod
    def change_local_ip(ip: str) -> str:
        m = re.compile(r"(\d+\.\d+\.\d+\.\d+)(?:/(\d+))?(?::(\d+))?").match(ip)
        if m:
            (_ip, net, port) = m.groups()
            if _ip is not None and net is not None:
                ips = IOTBaseCommon.get_networks(ip)

                __ip = f"{_ip}/{net}"
                ip_start = ip_address(str(ip_network(__ip, False)).split('/')[0])
                ip_end = ip_network(__ip, False).broadcast_address
                for k, v in psutil.net_if_addrs().items():
                    for item in v:
                        if item[0] == 2:
                            item_ip = item[1]
                            if ':' not in item_ip:
                                item_ip = str(item_ip)
                                if item_ip in ips:
                                    return f"{item_ip}:47808" if port is None else f"{item_ip}:{port}"  # 不带net return ip.replace(_ip, str(item_ip)) # 不带net
        return ip

    @staticmethod
    def check_ip(ip: str):
        p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
        if p.match(ip):
            return True
        return False

    @staticmethod
    def send_request(url: str, method: Optional[str] = None, params: Union[str, JsonType, None] = None, data: Union[str, JsonType, None] = None, files: Union[str, JsonType, None] = None, headers: Optional[dict] = None, cookies: Optional[dict] = None, auth: Optional[AuthBase] = None, encoding: Optional[str] = None, raise_error: Optional[bool] = None, retry: Optional[int] = None, timeout: Optional[int] = None) -> Response:
        if headers is None:
            headers = {}
        raise_error = False if raise_error is None else raise_error
        retry = 1 if retry is None else retry
        method = 'POST' if method is None else method.upper()
        timeout = 60 if timeout is None else timeout
        encoding = 'utf-8' if encoding is None else encoding

        payload = data
        last_error = None
        for i in range(0, retry):
            try:
                if method == 'GET':
                    response = requests.get(url=url, headers=headers, timeout=timeout, auth=auth, verify=False)
                elif method == 'POST':
                    response = requests.post(url=url, headers=headers, files=files, data=payload, params=params, timeout=timeout, auth=auth, verify=False)
                else:
                    raise NotImplementedError(f"Method {method} is not supported yet.")
                if response.status_code == 200:
                    response.encoding = encoding
                    return IOTBaseCommon.Response(True, '1', '', response.text, response.headers)
                raise Exception(f'Unexpected result: {response.status_code} {response.text}')
            except Exception as e:
                last_error = e
        if raise_error:
            raise last_error
        else:
            return IOTBaseCommon.Response(False, '0', last_error.__str__(), None, None)

    @staticmethod
    def format_name(name: str, pattern: str = r'[^a-zA-Z0-9_]+', replace: str = '_'):
        if name is None:
            return ''
        else:
            return re.sub(r'^_|_$', '', re.sub(pattern, replace, name.strip()))

    @staticmethod
    def format_value(value: Union[str, int, float]):
        if isinstance(value, str):
            try:
                dec_value = Decimal(value)
                return int(float(value)) if dec_value == dec_value.to_integral() else float(value)
            except:
                pass
        return value

    @staticmethod
    def get_timestamp():
        return time.time()

    @staticmethod
    def get_pid():
        return os.getpid()

    @staticmethod
    def get_file_folder(file_path: str):
        return os.path.dirname(file_path)

    @staticmethod
    def get_file_name(file_path: str):
        return os.path.basename(file_path)

    @staticmethod
    def check_file_exist(file_path: str):
        return os.path.exists(file_path)

    @staticmethod
    def is_windows() -> bool:
        return platform.system().lower() == 'windows'

    @staticmethod
    def set_timeout_wrapper(timeout):
        def inner_set_timeout_wrapper(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func_timeout(timeout, func, args=args, kwargs=kwargs)
                except FunctionTimedOut as e:
                    raise Exception(f'func({func.__name__}) time out')
                except Exception as e:
                    raise e

            return wrapper

        return inner_set_timeout_wrapper


class IOTPoint:

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __str__(self):
        pass

    def get(self, key: str, default=None):
        return self.kwargs.get(key, default)

    def set(self, key: str, value):
        self.kwargs[key] = value


class IOTSimulateObject:

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def update(self, **kwargs):
        self.kwargs.update(kwargs)

    def get(self, key: str, default=None):
        return self.kwargs.get(key, default)

    def set(self, key: str, value):
        self.kwargs[key] = value

    def has_key(self, key: str) -> bool:
        return True if key in self.kwargs.keys() else False


class IOTDriver:

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.uuid = uuid.uuid1()
        self.reinit_flag = True  # 重新初始化
        self.configs = {}
        self.points = {}
        self.enable = True
        self.exit_flag = False

        self.client = None
        self.clients = None
        self.server = None
        self.servers = None

        self.infos = {}     # 信息
        self.logs = []      # 日志信息

        self.callbacks = {}     # 回调函数

        self.configure(**kwargs)

        self.update_info(uuid=self.uuid, start=IOTBaseCommon.get_datetime_str())

    def __del__(self):
        self.exit()

    def __str__(self):
        return f"{self.__class__.__name__}({self.uuid})"

    @abstractmethod
    def exit(self):
        raise NotImplementedError()

    @abstractmethod
    def reinit(self):
        raise NotImplementedError()

    @classmethod
    def template(cls, mode: int, type: str, lan: str):
        raise NotImplementedError()

    @abstractmethod
    def read(self, **kwargs):
        raise NotImplementedError()

    def write(self, **kwargs):
        raise NotImplementedError()

    def update(self, **kwargs):
        self.kwargs.update(kwargs)
        self.configure(**kwargs)

    def configure(self, **kwargs):
        if 'configs' in kwargs.keys():
            self.configs = kwargs.get('configs')

        if 'points' in kwargs.keys():
            points = kwargs.get('points')
            self.points = {}
            for name, point in points.items():
                self.points[name] = IOTPoint(**point)

        self.reinit_flag = True

    def scan(self, **kwargs):
        raise NotImplementedError()

    def ping(self, **kwargs) -> bool:
        return True

    def logging(self, **kwargs):
        if 'call_logging' in kwargs.keys():
            self.callbacks['call_logging'] = kwargs.get('call_logging')

        if 'content' in kwargs.keys():
            call_logging = self.callbacks.get('call_logging')
            if call_logging:
                call_logging(**kwargs)
            self.save_log(kwargs.get('content'))

    def simulate(self, **kwargs):
        raise NotImplementedError()

    def info(self, **kwargs) -> dict:
        return self.infos

    def status(self, **kwargs) -> bool:
        return self.enable

    def discover(self, **kwargs):
        pass

    def delay(self, delay: Union[int, float] = 1):
        if isinstance(delay, int):
            while self.kwargs.get('enabled', True) is True and delay > 0:
                time.sleep(1)
                delay = delay - 1
        elif isinstance(delay, float):
            _delay = int(delay)
            while self.kwargs.get('enabled', True) is True and _delay > 0:
                time.sleep(1)
                _delay = _delay - 1
            time.sleep(delay - _delay)

    def save_log(self, log_content: str):
        if isinstance(log_content, str) and len(log_content) > 0:
            if len(self.logs) >= 500:
                self.logs.pop(0)
            self.logs.append(log_content)

    def update_info(self, **kwargs):
        self.infos.update(**kwargs)

    def create_point(self, **kwargs) -> dict:
        point = {}
        templates = self.template(0, 'point', 'en')
        for template in templates:
            point[template.get('code')] = template.get('default')
        point.update(**kwargs)
        return point
