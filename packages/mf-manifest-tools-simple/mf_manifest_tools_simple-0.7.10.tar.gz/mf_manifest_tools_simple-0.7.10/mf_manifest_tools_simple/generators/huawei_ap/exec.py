import os
import re
import subprocess
from string import Template

from inflection import underscore
from loguru import logger

from mf_manifest_tools_simple.data_struct import MFManifest

__all__ = ["HuaweiAPExecGenerator"]


def subscriber_helper(swc):
    return 'ap::APSubscriber<{proxy}> {var}("{instance_specifier}", "{id}");'.format(
        proxy=swc["proxy"],
        data_type=swc["data_type"],
        instance_specifier=swc["instance_specifier"],
        id=swc["key"],
        var=swc["var"])


def publisher_helper(swc):
    return 'ap::APPublisher<{skeleton}> {var}("{instance_identifier}");'.format(
        skeleton=swc["skeleton"],
        data_type=swc["data_type"],
        instance_identifier=swc["key"],
        var=swc["var"])


def sub_callback_helper(swc):
    return '{var}.setCallback([&](const {data_type}* src){{{maf_data_type} dst{{}}; FROM_AP(src, dst);\n/* TODO: Process dst */}});'.format(
        var=swc["var"],
        data_type=swc["data_type"],
        maf_data_type=swc["maf_data_type"])


def ros_publisher_helper(swc):
    return 'auto ros_{var} = nh.advertise<{ros_msg_type}>("{topic_name}", 3);'.format(
        var=swc["var"],
        ros_msg_type=swc["ros_msg_type"],
        topic_name=swc["ros_topic"])


def ros_header_helper(swc):
    return '#include "{ros_header_file}/ros_cpp_struct_convert.hpp"'.format(
        ros_header_file=swc["ros_header_file"])


def ros_subscriber_helper(swc):
    return 'ros_{var} = std::make_shared<ros::Subscriber>(nh.subscribe<{ros_msg_type}>("{topic_name}", 3, [&](const {ros_msg_type}ConstPtr &src) \
{{{maf_data_type} dst{{}}; ros_cpp_struct_convert::from_ros(*src, dst);}}));'.format(
        var=swc["var"],
        ros_msg_type=swc["ros_msg_type"],
        topic_name=swc["ros_topic"],
        handle_name="",
        maf_data_type=swc["maf_data_type"])


def ros_subscriber_declaration_helper(swc):
    return 'std::shared_ptr<ros::Subscriber> ros_{var};'.format(var=swc["var"])


class HuaweiAPExecGenerator(object):
    @staticmethod
    def generate(data: MFManifest, output_dir: str):
        for swc in data.swcs:
            swcRoot = swc.name + "Exec/executable.h"
            main_template = open(
                os.path.join(
                    os.path.abspath(
                        os.path.join(os.path.realpath(__file__), "..")),
                    "main.template"), "r").read()
            subscribers = []
            publishers = []
            sub_callbacks = []
            ros_subscribers = []
            ros_subscriber_declarations = []
            ros_publishers = []
            ros_topics = []
            ros_headers = []
            ros_header_files = []
            # sub instance
            for connection in data.connections:
                if connection.receiver_swc.name != swc.name or "HUAWEI-MDC" not in connection.instance.topic.platforms:
                    continue
                if connection.sender_swc.name == "mfr2ap_adaptor":
                    continue
                SWC = {}
                datatype = connection.instance.datatype
                struct_name = datatype.c_ref.struct.split("::")
                SWC["proxy"] = "ap_" + struct_name[0] + "::" + underscore(
                    struct_name[1]
                ) + "_service_interface" + (
                    "_someip" if connection.topic.huawei_ref.is_someip else "") + "::proxy::" + datatype.name + "ServiceInterface" + (
                    "SomeIp" if connection.topic.huawei_ref.is_someip else "") + "Proxy"
                SWC["data_type"] = "ap_" + datatype.c_ref.struct
                SWC["id"] = connection.instance.instance_id
                SWC["key"] = "/".join([
                    connection.instance.datatype.name,
                    connection.instance.topic.topic_name,
                    connection.instance.sender_swc.name
                ])
                SWC[
                    "instance_specifier"] = swc.name + "Exec/" + swc.name + "Root/" + swc.name + "Sub" + datatype.name + (
                    "SomeIp" if connection.topic.huawei_ref.is_someip else "")
                SWC["var"] = "sub_" + underscore(
                    connection.topic.topic_name) + "_by_" + underscore(
                    connection.sender_swc.name)
                SWC["maf_data_type"] = datatype.c_ref.struct
                SWC["ros_topic"] = connection.topic.ros_ref.ros_topic
                SWC["ros_msg_type"] = re.sub(
                    r'::', "_msgs::",
                    re.sub(r'^maf_', "", datatype.c_ref.struct))
                SWC["ros_header_file"] = re.sub(
                    r'::.*', "_msgs",
                    re.sub(r'^maf_', "", datatype.c_ref.struct))
                sub_callbacks.append(sub_callback_helper(SWC))
                subscribers.append(subscriber_helper(SWC))
                if SWC["ros_topic"] not in ros_topics:
                    ros_topics.append(SWC["ros_topic"])
                    ros_subscribers.append(ros_subscriber_helper(SWC))
                    ros_subscriber_declarations.append(
                        ros_subscriber_declaration_helper(SWC))
                if SWC["ros_header_file"] not in ros_headers:
                    ros_headers.append(SWC["ros_header_file"])
                    ros_header_files.append(ros_header_helper(SWC))

            # #pub instance
            for instance in data.service_instances:
                if instance.sender_swc.name != swc.name or "HUAWEI-MDC" not in instance.topic.platforms:
                    continue
                SWC = {}
                datatype = instance.datatype
                struct_name = datatype.c_ref.struct.split("::")
                SWC["skeleton"] = "ap_" + struct_name[0] + "::" + underscore(
                    struct_name[1]
                ) + "_service_interface" + (
                    "_someip" if instance.topic.huawei_ref.is_someip else "") + "::skeleton::" + datatype.name + "ServiceInterface" + (
                    "SomeIp" if instance.topic.huawei_ref.is_someip else "") + "Skeleton"
                SWC["data_type"] = "ap_" + datatype.c_ref.struct
                SWC["var"] = "pub_" + underscore(instance.topic.topic_name)
                SWC["instance_identifier"] = instance.instance_id
                SWC["key"] = "/".join([
                    instance.datatype.name, instance.topic.topic_name,
                    instance.sender_swc.name
                ])
                SWC["ros_topic"] = instance.topic.ros_ref.ros_topic
                SWC["ros_msg_type"] = re.sub(
                    r'::', "_msgs::",
                    re.sub(r'^maf_', "", datatype.c_ref.struct))
                SWC["ros_header_file"] = re.sub(
                    r'::.*', "_msgs",
                    re.sub(r'^maf_', "", datatype.c_ref.struct))
                publishers.append(publisher_helper(SWC))

                ros_publishers.append(ros_publisher_helper(SWC))
                if SWC["ros_header_file"] not in ros_headers:
                    ros_headers.append(SWC["ros_header_file"])
                    ros_header_files.append(ros_header_helper(SWC))

            need_dict = {
                "swcRoot":
                    swcRoot,
                "subscribers":
                    "\n".join(subscribers),
                "publishers":
                    "\n".join(publishers),
                "sub_callback":
                    "\n".join(sub_callbacks),
                "ros_subscribers":
                    "\n".join(ros_subscribers),
                "ros_subscriber_declarations":
                    "\n".join(ros_subscriber_declarations),
                "ros_publishers":
                    "\n".join(ros_publishers),
                "ros_headers":
                    "\n".join(ros_header_files),
                "swcName":
                    swc.name
            }
            path = os.path.join(output_dir, swc.name + ".cc")
            with open(path, "w") as f:
                f.write(Template(main_template).substitute(need_dict))

            # Clang-format
            try:
                subprocess.check_call(["clang-format", "-i", path])
            except:
                logger.warning("Clang format failed")
