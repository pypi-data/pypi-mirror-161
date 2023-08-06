from dataclasses import dataclass, field
from typing import List

__all__ = ["MFManifest", "MFDataType", "MFDataTypeCRef", "MFDataTypeROSRef", "MFTopicROSRef", "MFTopic", "MFPort",
           "MFSWC", "MFConnection", "MFDataTypeHuaweiRef", "MFServiceInstance", "MFTopicMFRRef", "MFPortHuaweiRef",
           "MFSWCHuaweiRef", "MFComplementary", "MFTopicMotionwiseRef", "MFTopicHuaweiRef", "MFSWCEnv"]


@dataclass
class MFDataTypeCRef(object):
    available: bool = False
    file: str = ""
    struct: str = ""


@dataclass
class MFDataTypeROSRef(object):
    available: bool = False
    package: str = ""
    struct: str = ""


@dataclass
class MFDataTypeHuaweiRef(object):
    interface_id: int = -1


@dataclass
class MFDataType(object):
    name: str = ""
    c_ref: MFDataTypeCRef = field(default_factory=MFDataTypeCRef)
    ros_ref: MFDataTypeROSRef = field(default_factory=MFDataTypeROSRef)
    huawei_ref: MFDataTypeHuaweiRef = field(default_factory=MFDataTypeHuaweiRef)
    frag_size: int = -1
    list_size: int = -1


@dataclass
class MFTopicROSRef(object):
    available: bool = False
    ros_topic: str = ""


@dataclass
class MFTopicMFRRef(object):
    available: bool = False
    mfr_topic: str = ""


@dataclass
class MFPort(object):
    topic_name: str = ""


@dataclass
class MFPortHuaweiRef(object):
    datatype_name: str = ""
    service_interface: str = ""
    instance_id: str = ""
    transport_plugin: str = ""
    service_interface_deployment: str = ""
    event_deployment: str = ""
    domain_id: int = 0


@dataclass
class MFSWCEnv(object):
    name: str = ""
    value: str = ""


@dataclass
class MFSWCHuaweiRef(object):
    is_in_aos_core: bool = False


@dataclass
class MFComplementary(object):
    name: str = ""
    # 接口或者模块task周期
    api_period: str = ""
    # 逻辑函数/Convert函数
    logic_convert_function: str = ""
    # 接口描述
    api_normal_description: str = ""
    api_abnormal_description: str = ""
    # 实现功能
    function_work: str = ""
    # 逻辑函数
    logic_function: str = ""
    # 输入
    inputs: List[str] = field(default_factory=list)
    # 输出
    outputs: List[str] = field(default_factory=list)
    # 返回值
    returns: List[str] = field(default_factory=list)
    # 最后一行的返回值
    last_return: str = ""


@dataclass
class MFSWC(object):
    name: str = ""
    group: str = ""
    envs: List[MFSWCEnv] = field(default_factory=list)
    huawei_ref: MFSWCHuaweiRef = field(default_factory=MFSWCHuaweiRef)
    sub_ports: List[MFPort] = field(default_factory=list)
    pub_ports: List[MFPort] = field(default_factory=list)
    sub_huawei_ports: List[MFPortHuaweiRef] = field(default_factory=list)
    pub_huawei_ports: List[MFPortHuaweiRef] = field(default_factory=list)
    complementary: MFComplementary = field(default_factory=MFComplementary)
    memory_usage: str = ""
    cpu_usage: str = ""
    function_description: str = ""
    affinitiy: List[int] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

    def filter_sub_topic(self, topic_name: str):
        res = filter(lambda x: x.topic_name == topic_name, self.sub_ports)
        try:
            return next(res)
        except StopIteration:
            return None


@dataclass
class MFTopicMotionwiseRef(object):
    rte: str = ""


@dataclass
class MFTopicHuaweiRef(object):
    is_someip: bool = False
    domain_id: int = 0


@dataclass
class MFTopic(object):
    topic_name: str = ""
    datatype: str = ""
    senders: List[MFSWC] = field(default_factory=list)
    receivers: List[MFSWC] = field(default_factory=list)
    ros_ref: MFTopicROSRef = field(default_factory=MFTopicROSRef)
    mfr_ref: MFTopicMFRRef = field(default_factory=MFTopicMFRRef)
    motionwise_ref: MFTopicMotionwiseRef = field(default_factory=MFTopicMotionwiseRef)
    platforms: List[str] = field(default_factory=list)
    huawei_ref: MFTopicHuaweiRef = field(default_factory=MFTopicHuaweiRef)


@dataclass
class MFServiceInstance(object):
    instance_id: int = -1
    sender_swc: MFSWC = field(default_factory=MFSWC)
    topic: MFTopic = field(default_factory=MFTopic)
    datatype: MFDataType = field(default_factory=MFDataType)

    def __eq__(self, other):
        return other.instance_id == self.instance_id and other.sender_swc.name == self.sender_swc.name and other.topic.topic_name == self.topic.topic_name and other.datatype.name == self.datatype.name

    def __repr__(self):
        return "MFServiceInstance(datatype <{}> id <{}> topic <{}> sent by <{}>)".format(self.datatype.name,
                                                                                         self.instance_id,
                                                                                         self.topic.topic_name,
                                                                                         self.sender_swc.name)


@dataclass
class MFConnection(object):
    sender_swc: MFSWC = field(default_factory=MFSWC)
    receiver_swc: MFSWC = field(default_factory=MFSWC)
    topic: MFTopic = field(default_factory=MFTopic)
    datatype: MFDataType = field(default_factory=MFDataType)
    instance: MFServiceInstance = field(default_factory=MFServiceInstance)

    def __repr__(self):
        return "MFConnection(from <{}> to <{}>, Datatype: <{}>)".format(self.sender_swc.name, self.receiver_swc.name,
                                                                        self.datatype.name)


@dataclass
class MFManifest(object):
    datatypes: List[MFDataType] = field(default_factory=list)
    topics: List[MFTopic] = field(default_factory=list)
    swcs: List[MFSWC] = field(default_factory=list)
    connections: List[MFConnection] = field(default_factory=list)
    service_instances: List[MFServiceInstance] = field(default_factory=list)
    complementaries: List[MFComplementary] = field(default_factory=list)

    def is_datatype_referenced(self, datatype_name: str):
        for swc in self.swcs:
            for port in swc.sub_ports:
                if self.filter_topic(port.topic_name).datatype == datatype_name:
                    return True
            for port in swc.pub_ports:
                if self.filter_topic(port.topic_name).datatype == datatype_name:
                    return True
        return False

    def filter_topic(self, topic_name: str):
        res = filter(lambda x: x.topic_name == topic_name, self.topics)
        try:
            return next(res)
        except StopIteration:
            return None

    def filter_datatype(self, name: str):
        res = filter(lambda x: x.name == name, self.datatypes)
        try:
            return next(res)
        except StopIteration:
            return None

    def filter_service_instance(self, sender_swc: str, topic_name: str, datatype_name: str):
        res = filter(lambda
                         x: x.sender_swc.name == sender_swc and x.topic.topic_name == topic_name and
                            x.datatype.name == datatype_name,
                     self.service_instances)
        try:
            return next(res)
        except StopIteration:
            return None

    def filter_swc(self, name: str):
        res = filter(lambda x: x.name == name, self.swcs)
        try:
            return next(res)
        except StopIteration:
            return None
