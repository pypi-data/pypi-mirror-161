import json

from mf_manifest_tools_simple.data_struct import MFManifest

__all__ = ["HuaweiAPSWCDatatypesGenerator"]


class HuaweiAPSWCDatatypesGenerator(object):
    @staticmethod
    def generate(data: MFManifest):
        ret = {"swcs": [], "instances": []}
        for swc in data.swcs:
            datatype_set = []
            for sub_port in swc.sub_ports:
                if data.filter_topic(sub_port.topic_name).datatype not in datatype_set:
                    datatype_set.append(data.filter_topic(sub_port.topic_name).datatype)
            for pub_port in swc.pub_ports:
                if data.filter_topic(pub_port.topic_name).datatype not in datatype_set:
                    datatype_set.append(data.filter_topic(pub_port.topic_name).datatype)
            curr_data = {"name": swc.name, "datatypes": []}
            for datatype in datatype_set:
                dt = data.filter_datatype(datatype)
                struct_name = dt.c_ref.struct.split("::")
                curr_data["datatypes"].append({
                    "header_file": dt.c_ref.file,
                    "namespace": struct_name[0],
                    "struct": struct_name[1]
                })
            ret["swcs"].append(curr_data)
        for instance in data.service_instances:
            ret["instances"].append({
                "instance_id": instance.instance_id,
                "topic": instance.topic.topic_name,
                "datatype": instance.datatype.name,
                "sender_swc": instance.sender_swc.name,
                "key": "/".join([instance.datatype.name, instance.topic.topic_name, instance.sender_swc.name])
            })
        return json.dumps(ret, indent=4).encode()
