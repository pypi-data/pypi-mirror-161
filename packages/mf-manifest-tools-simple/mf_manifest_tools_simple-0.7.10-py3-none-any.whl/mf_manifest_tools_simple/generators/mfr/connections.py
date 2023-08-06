import yaml

from mf_manifest_tools_simple.data_struct import MFManifest

__all__ = ["MFRConnectionsGenerator"]


class MFRConnectionsGenerator(object):
    @staticmethod
    def generate(data: MFManifest):
        doc = {"manifest": []}
        for conn in data.connections:
            if conn.topic.mfr_ref.available:
                structs = conn.datatype.c_ref.struct.split("::")
                datatype = structs[0] + "_mfrmsgs/MFRMessage" + structs[1]
                doc["manifest"].append({
                    "publisher": conn.sender_swc.name,
                    "subscriber": conn.receiver_swc.name,
                    "topic": conn.topic.mfr_ref.mfr_topic,
                    "data_type": datatype
                })
        return yaml.dump(doc)
