import logging

from scapy.fields import ByteEnumField, BitEnumField, BitField, ConditionalField, Field, PacketField, LEShortField, FlagsField, ShortField, XByteField, XIntField, ByteField, PacketListField
from scapy.packet import Packet, Padding, NoPayload
from struct import unpack, pack
from typing import List, Dict, Any
from threading import Event

from .base import IOTBaseCommon, IOTDriver

'''
pip install scapy==2.4.5
'''

'''
ACPI
	68(1)
	长度(1)
	控制域(4)
		I帧
			发送序号， 接收序号
		S帧
			01 00 接收序号
		U帧
			0x 00 00 00
ASDU
	类型(1)
		监视方向
			1 单点遥信（带品质 不带时标）
			2 双点遥信
			13 段浮点遥测（带品质 不带时标）
		控制方向
			45 单点遥控
		监视方向系统类型
			70 初始化结束
		控制方向系统类型
			100 总召
			101 累积量召唤
			102 读命令
			103 时钟同步
	限定词(1)
		SQ = 0 地址连续 SQ=1地址不连续
	传送原因(2)
		PN
			6 激活
			7 激活确认
			8 停止激活
	地址(2)
	(信息体)(长度-10)
		连续信息传输型
            带绝对时标（遥测）
                地址编号(3字节) 信息体数据 品质描述词(1字节) 重复 信息体数据 品质描述词(1字节) 绝对时标(7字节)
            不带绝对时标（遥测）
                地址编号(3字节) 信息体数据 品质描述词(1字节) 重复 信息体数据 品质描述词(1字节)
            带绝对时标（遥信）
                地址编号(3字节) 信息体数据(1字节) 重复 信息体数据(1字节) 绝对时标(7字节)
            不带绝对时标（遥信）
                地址编号(3字节) 信息体数据(1字节) 重复 信息体数据(1字节)
        非连续信息传输型
            带绝对时标（遥测）
                地址编号(3字节) 信息体数据 品质描述词(1字节) 重复 地址编号(3字节) 信息体数据 品质描述词(1字节) 绝对时标(7字节)
            不带绝对时标（遥测）
                地址编号(3字节) 信息体数据 品质描述词(1字节) 重复 地址编号(3字节) 信息体数据 品质描述词(1字节)
            带绝对时标（遥信）
                地址编号(3字节) 信息体数据(1字节) 重复 地址编号(3字节) 信息体数据(1字节) 绝对时标(7字节)
            不带绝对时标（遥信）
                地址编号(3字节) 信息体数据(1字节) 重复 地址编号(3字节) 信息体数据(1字节)
                
        遥控和设定值
            单点遥控(1字节)   (S/E QU[6:2] RES SCS)
                S/E = 0 遥控执行命令；S/E=1 遥控选择命令；
                QU = 0 被控占内部确定遥控输出方式，不有控制站选择；
                    1 短脉冲方式输出
                    2 长脉冲方式输出
                    3 持续脉冲方式输出
                其他值没有定义
                RES ：保留位
                SCS ： 设置值； 0 = 控开 ；1 = 控合 
            双电遥控(1字节)   (S/E QU[6:2] DCS)
                S/E = 0 遥控执行命令；S/E=1 遥控选择命令；
                QU = 0 被控占内部确定遥控输出方式，不有控制站选择；
                    1 短脉冲方式输出
                    2 长脉冲方式输出
                    3 持续脉冲方式输出
                DCS； 0 无效控制
                    1 控分
                    2 控合
                    3 无效控制
            设定值QOS
		
'''


class IECDefine:

    # 类型标识(1字节)
    ASDU_TYPE = {
        0x01: 'M_SP_NA_1',  # 单点遥信(带品质描述 不带时标)
        0x03: 'M_DP_NA_1',  # 双点遥信(带品质描述 不带时标)
        0x05: 'M_ST_NA_1',  # 步位置信息(带品质描述 不带时标)
        0x07: 'M_BO_NA_1',  # 32比特串(带品质描述 不带时标)
        0x09: 'M_ME_NA_1',  # 规一化遥测值(带品质描述 不带时标)
        0x0B: 'M_ME_NB_1',  # 标度化遥测值(带品质描述 不带时标)
        0x0D: 'M_ME_NC_1',  # 短浮点遥测值(带品质描述 不带时标)
        0x0F: 'M_IT_NA_1',  # 累积量(带品质描述 不带时标)
        0x14: 'M_PS_NA_1',  # 成组单点遥信(只带变量标志)
        0x15: 'M_ME_ND_1',  # 规一化遥测值(不带品质描述 不带时标)
        0x1E: 'M_SP_TB_1',  # 单点遥信(带品质描述 带绝对时标)
        0x1F: 'M_DP_TB_1',  # 双点遥信(带品质描述 带绝对时标)
        0x20: 'M_ST_TB_1',  # 步位置信息(带品质描述 带绝对时标)
        0x21: 'M_BO_TB_1',  # 32比特串(带品质描述 带绝对时标)
        0x22: 'M_ME_TD_1',  # 规一化遥测值(带品质描述 带绝对时标)
        0x23: 'M_ME_TE_1',  # 标度化遥测值(带品质描述 带绝对时标)
        0x24: 'M_ME_TF_1',  # 短浮点遥测值(带品质描述 带绝对时标)
        0x25: 'M_IT_TB_1',  # 累积量(带品质描述 带绝对时标)
        0x26: 'M_EP_TD_1',  # 继电保护装置事件(带品质描述 带绝对时标)
        0x27: 'M_EP_TE_1',  # 继电保护装置成组启动事件(带品质描述 带绝对时标)
        0x28: 'M_EP_TF_1',  # 继电保护装置成组出口信息(带品质描述 带绝对时标)
        0x2D: 'C_SC_NA_1',  # 单点遥控(一个报文只有一个遥控信息体 不带时标)
        0x2E: 'C_DC_NA_1',  # 双点遥控(一个报文只有一个遥控信息体 不带时标)
        0x2F: 'C_RC_NA_1',  # 升降遥控(一个报文只有一个遥控信息体 不带时标)
        0x30: 'C_SE_NA_1',  # 规一化设定值(一个报文只有一个设定值 不带时标)
        0x31: 'C_SE_NB_1',  # 标度化设定值(一个报文只有一个设定值 不带时标)
        0x32: 'C_SE_NC_1',  # 短浮点设定值(一个报文只有一个设定值 不带时标)
        0x33: 'C_SE_ND_1',  # 32比特串(一个报文只有一个设定值 不带时标)
        0x3A: 'C_SE_TA_1',  # 单点遥控(一个报文只有一个设定值 带时标)
        0x3B: 'C_SE_TB_1',  # 双点遥控(一个报文只有一个设定值 带时标)
        0x3C: 'C_SE_TC_1',  # 升降遥控(一个报文只有一个设定值 带时标)
        0x3D: 'C_SE_TD_1',  # 规一化设定值(一个报文只有一个设定值 带时标)
        0x3E: 'C_SE_TE_1',  # 标度化设定值(一个报文只有一个设定值 带时标)
        0x3F: 'C_SE_TF_1',  # 短浮点设定值(一个报文只有一个设定值 带时标)
        0x40: 'C_SE_TG_1',  # 32比特串(一个报文只有一个设定值 带时标)
        0x46: 'M_EI_NA_1',  # 初始化结束(从站发送，主站收到时候会做一次总召)
        0x64: 'C_IC_NA_1',  # 总召
        0x65: 'C_CI_NA_1',  # 累积量召唤
        0x66: 'C_RD_NA_1',  # 读命令
        0x67: 'C_CS_NA_1',  # 时钟同步命令
        0x69: 'C_RS_NA_1',  # 复位进程命令
        0x6B: 'C_TS_NA_1',  # 带时标的测试命令
        0x88: 'C_SE_NE_1',  # 规一化设定值(一个报文可以包含多个设定值 不带时标)
    }

    # 帧类型
    APCI_TYPE = {
        0x00: 'I',
        0x01: 'S',
        0x03: 'U'
    }

    # U帧类型
    APCI_U_TYPE = {
        0x01: 'STARTDT act',
        0x02: 'STARTDT con',
        0x04: 'STOPDT act',
        0x08: 'STOPDT con',
        0x10: 'TESTFR act',
        0x20: 'TESTFR con',
    }

    # 可变结构限定词(1字节)
    ASDU_SQ = {
        0X00: 0,
        0x80: 1  # 信息对象的地址连续 总召唤时，为了压缩信息传输时间SQ=
    }

    # 传送原因(2字节)
    ASDU_CAUSE = {
        0: 'not used',
        1: 'per/cyc',  # 周期 循环
        2: 'back',  # 背景扫描
        3: 'spont',  # 突发
        4: 'init',  # 初始化
        5: 'req',  # 请求或被请求
        6: 'act',  # 激活
        7: 'act config',  # 激活确认
        8: 'deact',  # 停止激活
        9: 'deact config',  # 停止激活确认
        10: 'act term',  # 激活终止
        11: 'retrem',  # 远方命令引起的返送信息
        12: 'retloc',  # 当地命令引起的返送信息
        13: 'file',
        20: 'inrogen',  # 响应站召唤
        21: 'inro1',  # 响应第1组召唤
        22: 'inro2',  # 响应第2组召唤
        23: 'inro3',
        24: 'inro4',
        25: 'inro5',
        26: 'inro6',
        27: 'inro7',
        28: 'inro8',
        29: 'inro9',
        30: 'inro10',
        31: 'inro11',
        32: 'inro12',
        33: 'inro13',
        34: 'inro14',
        35: 'inro15',
        36: 'inro16',
        37: 'reqcogen',  # 响应累积量站召唤
        38: 'reqco1',
        39: 'reqco2',
        40: 'reqco3',
        41: 'reqco4',
        44: 'unknown type identification',  # 未知的类型标识
        45: 'unknown cause of transmission',  # 未知的传送原因
        46: 'unknown common address of ASDU',  # 未知的应用服务数据单元公共地址
        47: 'unknown information object address'  # 未知的信息对象地址
    }

    # 传送原因 P/N
    ASDU_PN = {
        0x00: 'Positive confirm',
        0x40: 'Negative confirm'
    }

    # 遥测品质描述词
    ASDU_QDS_FLAGS = ['OV', '*', '*', '*', 'BL', 'SB', 'NT', 'IV']

    # 双点信息品质描述词
    ASDU_DIQ_FLAGS = ['*', '*', '*', '*', 'BL', 'SB', 'NT', 'IV']

    # 单点信息品质描述词
    ASDU_SIQ_FLAGS = ['SPI', '*', '*', '*', 'BL', 'SB', 'NT', 'IV']

    # 命令方式
    ASDU_SEL_EXEC = {
        0x00: 'Execute',
        0x80: 'Select',
        0x01: 'Select',
    }

    # 遥控输出方式
    ASDU_QU = {
        0x00: 'no pulse defined',
        0x01: 'short pulse duration (circuit-breaker)',  # 短脉冲方式输出
        0x02: 'long pulse duration',  # 长脉冲方式输出
        0x03: 'persistent output',  # 持续脉冲方式输出
        0x04: 'reserved',
        0x05: 'reserved',
        0x06: 'reserved',
    }

    # 设置值
    ASDU_SCS = {
        0x00: 'OFF',
        0x01: 'ON'
    }

    #
    ASDU_SU = {
        0X80: 'summer time',
        0x00: 'normal time'
    }

    # Day Of Week
    ASDU_DOW = {
        0x00: 'undefined',
        0x01: 'monday',
        0x02: 'tuesday',
        0x03: 'wednesday',
        0x04: 'thursday',
        0x05: 'friday',
        0x06: 'saturday',
        0x07: 'sunday'
    }

    ASDU_DPASDU_I = {
        0x00: 'Indeterminate or Intermediate state',
        0x01: 'Determined state OFF',
        0x02: 'Determined state ON',
        0x03: 'Indeterminate state'
    }

    ASDU_TRANSIENT = {
        0x00: 'not in transient',
        0x80: 'in transient'
    }

    ASDU_QOASDU_I_ENUM = {
        0x14: 'Station interrogation (global)',
        0x15: 'Interrogation of group 1',
        0x16: 'Interrogation of group 2',
        0x17: 'Interrogation of group 3',
        0x18: 'Interrogation of group 4',
        0x19: 'Interrogation of group 5',
        0x1A: 'Interrogation of group 6',
        0x1B: 'Interrogation of group 7',
        0x1C: 'Interrogation of group 8',
        0x1D: 'Interrogation of group 9',
        0x1E: 'Interrogation of group 10',
        0x1F: 'Interrogation of group 11',
        0x20: 'Interrogation of group 12',
        0x21: 'Interrogation of group 13',
        0x22: 'Interrogation of group 14',
        0x23: 'Interrogation of group 15',
        0x24: 'Interrogation of group 16'
    }

    ASDU_R_ENUM = {
        0x00: 'Local power switch on',
        0x01: 'Local manual reset',
        0x02: 'Remote reset',
    }

    for i in range(0x03, 0x7f):
        ASDU_R_ENUM[i] = 'Undefined'

    ASDU_I_ENUM = {
        0x00: 'Initialization with unchanged local parameters',
        0x80: 'Initialization after change of local parameters'
    }


class IECPacket:

    class COI(Packet):
        name = 'COI'
        fields_desc = [
            BitEnumField('I', None, 1, IECDefine.ASDU_I_ENUM),
            BitEnumField('R', None, 7, IECDefine.ASDU_R_ENUM),
        ]

    class VTI(Packet):
        name = 'VTI'
        fields_desc = [
            BitEnumField('Transient', None, 1, IECDefine.ASDU_TRANSIENT),
            BitField('Value', None, 7),
        ]

    class DIQ(Packet):
        name = 'QDS'
        fields_desc = [
            ByteEnumField('DPI', 0x00, IECDefine.ASDU_DPASDU_I),
            FlagsField('flags', 0x00, 8, IECDefine.ASDU_DIQ_FLAGS),
        ]

        def do_dissect(self, s):
            self.DPI = s[0] & 0x03
            self.flags = s[0] & 0xf0
            return s[1:]

        def do_build(self):
            s = list(range(1))
            s[0] = int(self.DPI) | int(self.flags)
            return bytes(s)

    class QOS(Packet):  # Section 7.2.6.39
        name = 'QOS'
        fields_desc = [
            BitEnumField('SE', 0x00, 1, IECDefine.ASDU_SEL_EXEC),
            BitField('QL', 0x00, 7),
        ]

    class CP56Time(Packet):
        name = 'CP56Time'
        fields_desc = [
            LEShortField('MS', 0),
            BitField('IV', 0, 1),
            BitField('RES1', 0, 1),
            BitField('Min', 0, 6),
            BitField('ASDU_SU', 0, 1),
            BitField('RES2', 0, 2),
            BitField('Hour', 0, 5),
            BitEnumField('DOW', 0, 3, IECDefine.ASDU_DOW),
            BitField('Day', 0, 5),
            BitField('RES3', 0, 4),
            BitField('Month', 0, 4),
            BitField('RES4', 0, 1),
            BitField('Year', 0, 7),
        ]

    class SCO(Packet):
        name = 'SCO'
        fields_desc = [
            BitEnumField('SE', 0, 1, IECDefine.ASDU_SEL_EXEC),
            BitEnumField('QU', 0, 6, IECDefine.ASDU_QU),
            BitEnumField('SCS', 0, 1, IECDefine.ASDU_SCS),
        ]

    class LEFloatField(Field):
        def __init__(self, name, default):
            Field.__init__(self, name, default, '<f')

    class LEIntField(Field):
        def __init__(self, name, default):
            Field.__init__(self, name, default, '<i')

    class SignedShortField(Field):
        def __init__(self, name, default):
            Field.__init__(self, name, default, "<h")

    class IOAID(Field):

        def __init__(self, name, default):
            Field.__init__(self, name, default, '<I')

        def addfield(self, pkt, s, val):
            if val is None:
                return s
            return s + pack('BBB', int(val & 0xff), int((val & 0xff00) / 0x0100), int((val & 0xff0000) / 0x010000))

        def getfield(self, pkt, s):
            return s[3:], self.m2i(pkt, unpack(self.fmt, s[:3] + b'\x00')[0])


class IECData:

    class IOA1(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            FlagsField('SIQ', 0x00, 8, IECDefine.ASDU_SIQ_FLAGS),
        ]

    class IOA3(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('DIQ', None, IECPacket.DIQ)
        ]

    class IOA5(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('VTI', None, IECPacket.VTI),
            FlagsField('QDS', 0x00, 8, IECDefine.ASDU_QDS_FLAGS),
        ]

    class IOA7(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            XIntField('BSI', 0x00000000),
            FlagsField('QDS', 0x00, 8, IECDefine.ASDU_QDS_FLAGS),
        ]

    class IOA9(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.SignedShortField('Value', None),
            FlagsField('QDS', 0x00, 8, IECDefine.ASDU_QDS_FLAGS),
        ]

    class IOA13(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.LEFloatField('Value', None),
            FlagsField('QDS', 0x00, 8, IECDefine.ASDU_QDS_FLAGS),
        ]

    class IOA30(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            FlagsField('SIQ', 0x00, 8, IECDefine.ASDU_SIQ_FLAGS),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

    class IOA31(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('DIQ', None, IECPacket.DIQ),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

    class IOA36(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.LEFloatField('Value', None),
            FlagsField('QDS', 0x00, 8, IECDefine.ASDU_QDS_FLAGS),
            PacketField('CP56Time', None, IECPacket.CP56Time),
        ]

    class IOA37(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.LEIntField('Binary_Counter', None),
            ByteField('SQ', 0),
            PacketField('CP56Time', None, IECPacket.CP56Time),
        ]

    class IOA45(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('SCO', None, IECPacket.SCO)
        ]

    class IOA50(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            IECPacket.LEFloatField('Value', None),
            PacketField('QOS', None, IECPacket.QOS)
        ]

    class IOA70(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('COI', None, IECPacket.COI),
        ]

    class IOA100(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            ByteEnumField('QOI', None, IECDefine.ASDU_QOASDU_I_ENUM),
        ]

    class IOA103(Packet):
        name = 'IOA'
        fields_desc = [
            IECPacket.IOAID('IOA', None),
            PacketField('CP56Time', None, IECPacket.CP56Time)
        ]

    IOAS = {
        1: IOA1,    # 单点遥信(带品质描述 不带时标)
        3: IOA3,    # 双点遥信(带品质描述 不带时标)
        5: IOA5,    # 步位置信息(带品质描述 不带时标)
        7: IOA7,    # 32比特串(带品质描述 不带时标)
        9: IOA9,    # 规一化遥测值(带品质描述 不带时标)
        13: IOA13,  # 短浮点遥测值(带品质描述 不带时标)
        30: IOA30,  # 单点遥信(带品质描述 带绝对时标)
        31: IOA31,  # 双点遥信(带品质描述 带绝对时标)
        36: IOA36,  # 短浮点遥测值(带品质描述 带绝对时标)
        37: IOA37,   # 累积量(带品质描述 带绝对时标)
        45: IOA45,  # 单点遥控(一个报文只有一个遥控信息体 不带时标)
        50: IOA50,   # 短浮点设定值(一个报文只有一个设定值 不带时标)
        70: IOA70,   # 初始化结束(从站发送，主站收到时候会做一次总召)
        100: IOA100,    # 总召
        103: IOA103,     # 时钟同步命令
    }

    IOALEN = {
        1: 4,
        3: 4,
        5: 5,
        7: 8,
        9: 6,
        13: 8,
        30: 10,
        31: 11,
        36: 15,
        37: 25,
        45: 4,
        50: 8,
        70: 4,
        100: 4,
        103: 10,
    }


class IOTIEC104(IOTDriver):

    class ASDU(Packet):
        name = 'ASDU'

        fields_desc = [
            ByteEnumField('Type', None, IECDefine.ASDU_TYPE),
            ByteEnumField('SQ', None, IECDefine.ASDU_SQ),
            ByteField('Num', 0),
            ByteEnumField('Cause', None, IECDefine.ASDU_CAUSE),
            ByteEnumField('PN', 0x00, IECDefine.ASDU_PN),
            ByteField('Test', None),
            ByteField('OA', None),
            LEShortField('Addr', None),
            PacketListField('IOA', None)
        ]

        def do_dissect(self, s):
            self.Type = s[0]    # 类型(1)
            self.SQ = s[1] & 0x80 == 0x80   # 限定词(1)
            self.Num = s[1] & 0x7f  # 数量
            self.Cause = s[2] & 0x3F    # 原因
            self.PN = s[2] & 0x40   # 第6位为P/N = 0 肯定 ； P/N = 1 否定 （正常为P/N = 0；P/N = 1说明该报文无效
            self.Test = s[2] & 0x80 # 第7为为测试 T = 0 未试验 ； T = 1 试验 （一般 T= 0）
            self.OA = s[3]          # 源发地址：用来记录来时哪个主站的响应数据，一般写 0；
            self.Addr = unpack('<H', s[4:6])[0] # 公共地址

            flag = True
            IOAS = list()
            remain = s[6:]
            idx = 6
            offset = 0
            if self.Type not in IECData.IOAS.keys():
                raise Exception(f"unsupport type({self.Type}")

            ioa_type = IECData.IOAS[self.Type]
            ioa_length = IECData.IOALEN[self.Type]
            if self.SQ:
                for i in range(1, self.Num + 1):
                    if flag:
                        IOAS.append(ioa_type(remain[:ioa_length]))
                        offset = IOAS[0].IOA
                        remain = remain[ioa_length:]
                        idx = idx + ioa_length
                        ioa_length = ioa_length - 3
                    else:
                        _offset = pack("<H", (i - 1) + offset) + b'\x00'  # See 7.2.2.1 of IEC 60870-5-101
                        IOAS.append(ioa_type(_offset + remain[:ioa_length]))
                        remain = remain[ioa_length:]
                        idx = idx + ioa_length
                    flag = False
            else:
                IOAS = [ioa_type(remain[(x * ioa_length):(x * ioa_length) + ioa_length]) for x in range(self.Num)]
                idx += ioa_length * self.Num
            self.IOA = IOAS
            return s[idx:]

        def do_build(self):
            s = bytearray()
            s.append(self.Type)
            s.append(self.SQ | self.Num)
            s.append(self.Test | self.PN | self.Cause)
            s.append(self.OA)
            s.append(int(self.Addr) & 0xff)
            s.append(int(self.Addr) >> 8)
            s = bytes(s)
            if self.IOA is not None:
                for i in self.IOA:
                    s += i.build()

            return s

        def info(self, pkt: Packet = None):
            pkt = self if pkt is None else pkt
            values = {}
            for key in pkt.fields.keys():
                if isinstance(pkt.fields[key], list):
                    for filed in pkt.fields[key]:
                        if isinstance(filed, Packet):
                            if pkt.name not in values.keys():
                                values[filed.name] = []
                            values[filed.name].append(self.info(filed))
                elif isinstance(pkt.fields[key], Packet):
                    values[pkt.fields[key].name] = self.info(pkt.fields[key])
                else:
                    values[key] = pkt.fields[key]
            return values

    class APCI(Packet):
        name = 'ACPI'

        fields_desc = [
            XByteField('START', 0x68),      # 68H
            ByteField('ApduLen', 4),        # 长度
            ByteEnumField('Type', 0x00, IECDefine.APCI_TYPE),   # 帧类型
            ConditionalField(XByteField('UType', None), lambda pkt: pkt.Type == 0x03),  # U帧类型
            ConditionalField(ShortField('Tx', 0x00), lambda pkt: pkt.Type == 0x00),
            ConditionalField(ShortField('Rx', 0x00), lambda pkt: pkt.Type < 3),
        ]

        def do_dissect(self, s):
            self.START = s[0]       # 68H
            self.ApduLen = s[1]     # 长度
            self.Type = s[2] & 0x03 if bool(s[2] & 0x01) else 0x00
            if self.Type == 3:      # U帧
                self.UType = (s[2] & 0xfc) >> 2
            else:
                if self.Type == 0:  # I帧
                    self.Tx = (s[3] << 7) | (s[2] >> 1)
                self.Rx = (s[5] << 7) | (s[4] >> 1)
            return s[6:]

        def dissect(self, s):
            s = self.pre_dissect(s)
            s = self.do_dissect(s)
            s = self.post_dissect(s)
            payl, pad = self.extract_padding(s)
            self.do_dissect_payload(payl)
            if pad:
                self.add_payload(IOTIEC104.APDU(pad))

        def do_build(self):
            s = list(range(6))
            s[0] = 0x68
            s[1] = self.ApduLen
            if self.Type == 0x03:
                s[2] = ((self.UType << 2) & 0xfc) | self.Type
                s[3] = 0
                s[4] = 0
                s[5] = 0
            else:
                if self.Type == 0x00:
                    s[2] = ((self.Tx << 1) & 0x00fe) | self.Type
                    s[3] = ((self.Tx << 1) & 0xff00) >> 8
                else:
                    s[2] = self.Type
                    s[3] = 0
                s[4] = (self.Rx << 1) & 0x00fe
                s[5] = ((self.Rx << 1) & 0xff00) >> 8
            s = bytes(s)
            if self.haslayer('ASDU'):
                s += self.payload.build()
            return s

        def extract_padding(self, s):
            if self.Type == 0x00 and self.ApduLen > 4:
                return s[:self.ApduLen - 4], s[self.ApduLen - 4:]
            return None, s

        def do_dissect_payload(self, s):
            if s is not None:
                p = IOTIEC104.ASDU(s, _internal=1, _underlayer=self)
                self.add_payload(p)

        def info(self):
            values = {}
            for key in self.fields.keys():
                values[key] = self.fields[key]
            return values

    class APDU(Packet):
        name = 'APDU'

        def dissect(self, s):

            s = self.pre_dissect(s)
            s = self.do_dissect(s)
            s = self.post_dissect(s)
            payl, pad = self.extract_padding(s)
            self.do_dissect_payload(payl)
            if pad:
                if pad[0] in [0x68]:
                    self.add_payload(IOTIEC104.APDU(pad, _internal=1, _underlayer=self))
                else:
                    self.add_payload(Padding(pad))

        def do_dissect(self, s):
            apci = IOTIEC104.APCI(s, _internal=1, _underlayer=self)
            self.add_payload(apci)

        def info(self):
            values = {}
            if not isinstance(self.payload, NoPayload):
                values[self.payload.name] = self.payload.info()
                if not isinstance(self.payload.payload, NoPayload):
                    values[self.payload.payload.name] = self.payload.payload.info()
            return values

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.reinit()

    def reinit(self):
        self.exit_flag = False
        self.values = {}
        self.send_count = 0
        self.recv_count = 0
        self.wait_event = None

    def exit(self):
        self.exit_flag = True
        if self.wait_event is not None:
            self.wait_event.set()

    @classmethod
    def template(cls, mode: int, type: str, lan: str) -> List[Dict[str, Any]]:
        templates = []
        if type == 'point':
            templates.extend([
                {'required': True, 'name': '是否可写' if lan == 'ch' else 'writable'.upper(), 'code': 'point_writable', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                {'required': True, 'name': '物理点名' if lan == 'ch' else 'name'.upper(), 'code': 'point_name', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''},
                {'required': True, 'name': '点地址' if lan == 'ch' else 'Address', 'code': 'point_address', 'type': 'int', 'default': 16385, 'enum': [], 'tip': ''},
                {'required': True, 'name': '点类型' if lan == 'ch' else 'Type'.upper(), 'code': 'point_type', 'type': 'int', 'default': 13, 'enum': [], 'tip': ''},
                {'required': False, 'name': '点描述' if lan == 'ch' else 'description'.upper(), 'code': 'point_description', 'type': 'string', 'default': 'Chiller_1_CHW_ENT', 'enum': [], 'tip': ''},
                {'required': False, 'name': '逻辑点名' if lan == 'ch' else 'name alias'.upper(), 'code': 'point_name_alias', 'type': 'string', 'default': 'Chiller_1_CHW_ENT1', 'enum': [], 'tip': ''},
                {'required': True, 'name': '是否启用' if lan == 'ch' else 'enable'.upper(), 'code': 'point_enabled', 'type': 'bool', 'default': 'TRUE', 'enum': [], 'tip': ''},
                {'required': True, 'name': '倍率' if lan == 'ch' else 'scale'.upper(), 'code': 'point_scale', 'type': 'string', 'default': '1', 'enum': [], 'tip': ''}
            ])
        elif type == 'config':
            templates.extend([
                {'required': True, 'name': '地址' if lan == 'ch' else 'Host', 'code': 'host', 'type': 'string', 'default': '192.168.1.1', 'enum': [], 'tip': ''},
                {'required': True, 'name': '端口' if lan == 'ch' else 'Port', 'code': 'port', 'type': 'int', 'default': 2404, 'enum': [], 'tip': ''},
                {'required': True, 'name': '超时(s)' if lan == 'ch' else 'Timeout(s)', 'code': 'timeout', 'type': 'float', 'default': 4, 'enum': [], 'tip': ''}
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
                type = point.get('point_type')  # 单点遥信
                address = point.get('point_address')    # 点地址
                if type is not None and address is not None:
                    if type not in read_items.keys():
                        read_items[type] = {}
                    read_items[type][address] = 1

        self._read(read_items)

        for name in names:
            point = self.points.get(name)
            if point:
                type = point.get('point_type')  # 单点遥信
                address = point.get('point_address')  # 点地址
                if type is not None and address is not None:
                    value = self.values.get(type, {}).get(address)
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
                type = point.get('point_type')  # 单点遥信
                address = point.get('point_address')  # 点地址
                if type is not None and address is not None:
                    results[name] = self._write(type, address, value)
            else:
                results[name] = [False, 'UnExist']
        return results

    def ping(self, **kwargs) -> bool:
        self.update_info(used=IOTBaseCommon.get_datetime_str())
        return True

    def _read(self, read_items: dict):
        if len(read_items) > 0 and self._get_client():
            self.wait_event = Event()
            self._send_zongzhao(self.client)
            try:
                self.wait_event.wait(30)
            except:
                pass

    def _write(self, type: int, address: int, value):
        raise NotImplementedError()

    def _release_client(self):
        try:
            if self.client:
                self.client.exit()
            self.client = None
        except Exception as e:
            pass

    def _get_client(self):
        if self.client is not None and self.client.check_invalid() is False:
            self._release_client()

        if self.client is None:
            client = IOTBaseCommon.IECSocketClient(self.configs.get('host'), self.configs.get('port'), self.configs.get('timeout', 4), callbacks={'handle_data': self.handle_data, 'handle_connect': self.handle_connect, 'handle_close': self.handle_close, 'handle_error': self.handle_error})
            self.client = client
        return self.client

    def handle_connect(self, client):
        start_frame = (IOTIEC104.APDU() / IOTIEC104.APCI(ApduLen=4, Type=0x03, UType=0x01)).build()
        self.logging(content=f"start act: [{client.format_bytes(start_frame)}]")

        # U帧启动报文
        client.send(start_frame)

    # 关闭事件
    def handle_close(self, client, reason: str):
        self.logging(content=f"({client}) close({reason})")

    def handle_error(self, client, e: Exception):
        logging.error(f"({client}) error({e.__str__()})")

    def _update_value(self, type_id: int, address: int, value):
        if type_id not in self.values.keys():
            self.values[type_id] = {}
        self.values[type_id][address] = value

    def handle_data(self, client, datas: bytes):
        try:
            if len(datas) > 0 and client is not None:
                info = IOTIEC104.APDU(datas).info()
                acpi = info.get('ACPI', {})
                asdu = info.get('ASDU', {})
                type = acpi.get('Type')
                if type == 0:  # I帧
                    self.recv_count = info.get('ACPI', {}).get('Rx', self.recv_count) + 1
                    type_id = asdu.get('Type')
                    cause_id = asdu.get('Cause')
                    self.logging(content=f"{self._get_frame_name(type_id, cause_id)}: [{self.client.format_bytes(datas)}]")

                    if type_id == 100:  # 总召
                        if cause_id == 7:   # 总召确认
                            pass
                        elif cause_id == 10:   # 总召结束
                            self.wait_event.set() # self._send_zongzhao(client)
                    elif type_id == 1:  # 单点遥信(带品质描述 不带时标)
                        for ioa in asdu.get('IOA', []):
                            if 'SIQ' in ioa.keys():
                                self._update_value(type_id, ioa.get('IOA'), ioa.get('SIQ').value)
                    elif type_id == 3:  # 双点遥信(带品质描述 不带时标)
                        pass
                    elif type_id == 5:  # 步位置信息(带品质描述 不带时标)
                        pass
                    elif type_id == 7:  # 32比特串(带品质描述 不带时标)
                        pass
                    elif type_id == 9:  # 规一化遥测值(带品质描述 不带时标)
                        pass
                    elif type_id == 13:     # 短浮点遥测值(带品质描述 不带时标)
                        for ioa in asdu.get('IOA', []):
                            if 'Value' in ioa.keys():
                                self._update_value(type_id, ioa.get('IOA'), ioa.get('Value'))
                    elif type_id == 30:  # 单点遥信(带品质描述 带绝对时标)
                        pass
                    elif type_id == 31:  # 双点遥信(带品质描述 带绝对时标)
                        pass
                    elif type_id == 36:  # 短浮点遥测值(带品质描述 带绝对时标)
                        pass
                    elif type_id == 37:  # 累积量(带品质描述 带绝对时标)
                        pass
                    elif type_id == 45:     # 单点遥控(一个报文只有一个遥控信息体 不带时标)
                        pass
                    elif type_id == 50:     # 短浮点设定值(一个报文只有一个设定值 不带时标)
                        pass

                elif type == 1:  # S帧
                    pass
                elif type == 3:
                    if info.get('ACPI', {}).get('UType') == 0x02:  # U帧激活确认
                        self.logging(content=f"start config: [{client.format_bytes(datas)}]")
                        self._send_zongzhao(client)
                    elif info.get('ACPI', {}).get('UType') == 0x08: # U帧结束确认
                        self.logging(content=f"start termin: [{client.format_bytes(datas)}]")
        except Exception as e:
            logging.error(f"handle data fail({e.__str__()})")

    def _send_frame(self, type_id: int, cause_id: int, datas: bytes):
        if self.client is not None:
            self.logging(content=f"{self._get_frame_name(type_id, cause_id)}: [{self.client.format_bytes(datas)}]")
            self.client.send(datas)
        
            if len(datas) > 6:
                self.send_count = self.send_count + 1
        else:
            raise Exception(f"no client")

    def _get_frame_name(self, type_id: int, cause_id: int) -> str:
        return f"{IECDefine.ASDU_TYPE[type_id]} {IECDefine.ASDU_CAUSE[cause_id]}"

    # 发送总召命令
    def _send_zongzhao(self, client):
        if client is not None:
            pkt = IOTIEC104.APDU()
            pkt /= IOTIEC104.APCI(ApduLen=14, Type=0x00, Tx=self.send_count, Rx=self.recv_count)
            pkt /= IOTIEC104.ASDU(Type=100, SQ=0, Cause=6, Num=1, Test=0, OA=0, Addr=1, IOA=[IECData.IOAS[100](IOA=0, QOI=0x14)])
            self._send_frame(100, 6, pkt.build())
