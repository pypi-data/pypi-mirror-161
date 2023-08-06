import json
import os
import re

import yaml
from jsonschema import validate
from loguru import logger

from mf_manifest_tools_simple.data_struct import *
from mf_manifest_tools_simple.exceptions import *

__all__ = ["ManifestYAMLParser"]


class ManifestYAMLParser(object):
    def __init__(self, filename: str, schema_file: str = ""):
        logger.info("Parsing {}", filename)
        if not schema_file:
            schema_file = os.path.dirname(os.path.realpath(__file__)) + "/manifest.schema.json"
        logger.debug("Using schema file: {}", schema_file)
        schema = json.load(open(schema_file, "r"))
        self._data = yaml.safe_load(open(filename))
        validate(instance=self._data, schema=schema)
        self._platforms = ["X86", "HUAWEI-MDC"]

    def _parse_affinity(self, s: str):
        matcher = re.compile(r"(\d+)\-(\d+)")
        ret = set()
        for it in s.split(","):
            it = it.strip()
            m = matcher.findall(it)
            if len(m) == 1:
                beg = int(m[0][0])
                end = int(m[0][1])
                if beg > end:
                    raise ManifestNotValid("Invalid affinity {}".format(s))
                for i in range(beg, end + 1):
                    ret.add(i)
            elif len(m) == 0:
                ret.add(int(it))
            else:
                raise ManifestNotValid("Invalid affinity {}".format(s))
        return sorted(list(ret))

    def parse_to_db(self, data: MFManifest):
        for dt in self._data.get("datatypes", []):
            datatype = MFDataType(name=dt["name"])
            if "huawei_ap" in dt and (
                    "list_size" in dt["huawei_ap"] or "frag_size" in dt["huawei_ap"]):
                try:
                    datatype.frag_size = dt["huawei_ap"].get("frag_size", -1)
                    datatype.list_size = dt["huawei_ap"].get("list_size", -1)
                    if datatype.frag_size <= 0 or datatype.list_size <= 0:
                        raise ValueError()
                except ValueError:
                    datatype.frag_size = -1
                    datatype.list_size = -1
                    raise ManifestNotValid("Datatype {} frag/list size invalid".format(datatype.name))
            if "huawei_ap" in dt and "interface_id" in dt["huawei_ap"]:
                datatype.huawei_ref.interface_id = dt["huawei_ap"]["interface_id"]
            datatype.c_ref = MFDataTypeCRef(True, dt["header_file"], dt["struct"])

            for exist_dt in data.datatypes:
                if exist_dt.c_ref.available and exist_dt.c_ref.file == datatype.c_ref.file and exist_dt.c_ref.struct == datatype.c_ref.struct:
                    logger.warning("Datatype {} and {} seems to be the same", datatype.name, dt.name)
            data.datatypes.append(datatype)
        for tp in self._data.get("topics", []):
            topic = MFTopic(topic_name=tp["name"], datatype=tp["datatype"])
            topic.mfr_ref = MFTopicMFRRef(True, tp["mfr_topic"])

            if "huawei_ap" in tp and "use_some_ip" in tp["huawei_ap"]:
                topic.huawei_ref.is_someip = tp["huawei_ap"]["use_some_ip"]
            if "huawei_ap" in tp and "domain_id" in tp["huawei_ap"]:
                topic.huawei_ref.domain_id = int(tp["huawei_ap"]["domain_id"])
            else:
                topic.huawei_ref.domain_id = 0
            topic.platforms = self._platforms
            data.topics.append(topic)
        for dt_swc in self._data.get("swcs", []):
            swc = MFSWC(name=dt_swc["name"])

            if "group" in dt_swc:
                swc.group = dt_swc["group"]

            if "envs" in dt_swc:
                for env in dt_swc["envs"]:
                    swc.envs.append(MFSWCEnv(name=env["name"], value=env["value"]))

            if "affinity" in dt_swc:
                swc.affinitiy = self._parse_affinity(dt_swc["affinity"])

            if "dependencies" in dt_swc:
                swc.dependencies = dt_swc["dependencies"]

            if "huawei_ap" in dt_swc:
                if "in_aos_core" in dt_swc["huawei_ap"]:
                    swc.huawei_ref.is_in_aos_core = dt_swc["huawei_ap"]["in_aos_core"]
                for sub_huawei_port in dt_swc["huawei_ap"].get("sub_huawei_ports", []):
                    swc.sub_huawei_ports.append(MFPortHuaweiRef(datatype_name=sub_huawei_port["datatype"],
                                                                service_interface=sub_huawei_port["service_interface"],
                                                                instance_id=sub_huawei_port["instance_id"],
                                                                transport_plugin=sub_huawei_port["transport_plugin"],
                                                                service_interface_deployment=sub_huawei_port[
                                                                    "service_interface_deployment"],
                                                                event_deployment=sub_huawei_port["event_deployment"],
                                                                domain_id=sub_huawei_port["domain_id"]))
                for pub_huawei_port in dt_swc["huawei_ap"].get("pub_huawei_ports", []):
                    swc.pub_huawei_ports.append(MFPortHuaweiRef(datatype_name=pub_huawei_port["datatype"],
                                                                service_interface=pub_huawei_port["service_interface"],
                                                                instance_id=pub_huawei_port["instance_id"],
                                                                transport_plugin=pub_huawei_port["transport_plugin"],
                                                                service_interface_deployment=pub_huawei_port[
                                                                    "service_interface_deployment"],
                                                                event_deployment=pub_huawei_port["event_deployment"],
                                                                domain_id=pub_huawei_port["domain_id"]))
            # Sub ports
            for sub_port in dt_swc.get("sub_ports", []):
                swc.sub_ports.append(MFPort(topic_name=sub_port["topic"]))

            # Pub ports
            for pub_port in dt_swc.get("pub_ports", []):
                swc.pub_ports.append(MFPort(topic_name=pub_port["topic"]))

            data.swcs.append(swc)
