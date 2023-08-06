import os

import yaml
from loguru import logger

from mf_manifest_tools_simple.data_struct import MFManifest

__all__ = ["MFManifestGenerator"]


class MFManifestGenerator:
    @staticmethod
    def generate(data: MFManifest, output_path: str):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            os.makedirs(output_path + "/swc")
            os.makedirs(output_path + "/topic")
            os.makedirs(output_path + "/datatype")
        if not os.path.isdir(output_path):
            raise Exception("Output path should be a directory")
        dt_dict = {}
        for datatype in data.datatypes:
            if datatype.c_ref.file not in dt_dict:
                dt_dict[datatype.c_ref.file] = {"datatypes": []}
            dt_dict[datatype.c_ref.file]["datatypes"].append({
                "name": datatype.name,
                "header_file": datatype.c_ref.file,
                "struct": datatype.c_ref.struct
            })
            if datatype.frag_size > 0 and datatype.list_size > 0:
                dt_dict[datatype.c_ref.file]["datatypes"][-1]["list_size"] = datatype.list_size
                dt_dict[datatype.c_ref.file]["datatypes"][-1]["frag_size"] = datatype.frag_size
        for dt_f in dt_dict:
            logger.info("Generating datatype file {}", dt_f.replace(".h", "").replace(".hpp", "") + ".yml")
            f = open(output_path + "/datatype/" + dt_f.replace(".h", "").replace(".hpp", "") + ".yml", "w")
            yaml.safe_dump(dt_dict[dt_f], f, sort_keys=False)
            f.close()

        topics = {"topics": []}
        for topic in data.topics:
            topics["topics"].append({
                "name": topic.topic_name,
                "datatype": topic.datatype,
            })
            if topic.huawei_ref.is_someip:
                topics["topics"][-1]["huawei_ap"] = {"use_some_ip": True}
            if topic.mfr_ref.mfr_topic:
                topics["topics"][-1]["mfr_topic"] = topic.mfr_ref.mfr_topic
            elif topic.ros_ref.ros_topic:
                topics["topics"][-1]["mfr_topic"] = topic.ros_ref.ros_topic
            else:
                topics["topics"][-1]["mfr_topic"] = ""
        logger.info("Generating topics file")
        f = open(output_path + "/topic/topics.yml", "w")
        yaml.safe_dump(topics, f, sort_keys=False)
        f.close()

        for swc in data.swcs:
            dt = {"name": swc.name}
            for sub_port in swc.sub_ports:
                if "sub_ports" not in dt:
                    dt["sub_ports"] = []
                dt["sub_ports"].append({
                    "topic": sub_port.topic_name
                })
            for pub_port in swc.pub_ports:
                if "pub_ports" not in dt:
                    dt["pub_ports"] = []
                dt["pub_ports"].append({
                    "topic": pub_port.topic_name
                })
            if swc.huawei_ref.is_in_aos_core or swc.sub_huawei_ports or swc.pub_huawei_ports:
                dt["huawei_ap"] = {}
                if swc.huawei_ref.is_in_aos_core:
                    dt["huawei_ap"]["in_aos_core"] = True
                for sub_huawei_port in swc.sub_huawei_ports:
                    if "sub_huawei_ports" not in dt["huawei_ap"]:
                        dt["huawei_ap"]["sub_huawei_ports"] = []
                    dt["huawei_ap"]["sub_huawei_ports"].append({
                        "datatype": sub_huawei_port.datatype_name,
                        "service_interface": sub_huawei_port.service_interface,
                        "service_interface_deployment": sub_huawei_port.service_interface_deployment,
                        "event_deployment": sub_huawei_port.event_deployment,
                        "transport_plugin": sub_huawei_port.transport_plugin,
                        "instance_id": sub_huawei_port.instance_id,
                        "domain_id": sub_huawei_port.domain_id
                    })
                for pub_huawei_port in swc.pub_huawei_ports:
                    if "pub_huawei_ports" not in dt["huawei_ap"]:
                        dt["huawei_ap"]["pub_huawei_ports"] = []
                    dt["huawei_ap"]["pub_huawei_ports"].append({
                        "datatype": pub_huawei_port.datatype_name,
                        "service_interface": pub_huawei_port.service_interface,
                        "service_interface_deployment": pub_huawei_port.service_interface_deployment,
                        "event_deployment": pub_huawei_port.event_deployment,
                        "transport_plugin": pub_huawei_port.transport_plugin,
                        "instance_id": pub_huawei_port.instance_id,
                        "domain_id": pub_huawei_port.domain_id
                    })
            logger.info("Generating swc file {}", swc.name + ".yml")
            f = open(output_path + "/swc/" + swc.name + ".yml", "w")
            yaml.safe_dump({"swcs": [dt]}, f, sort_keys=False)
            f.close()
        logger.success("Done")
