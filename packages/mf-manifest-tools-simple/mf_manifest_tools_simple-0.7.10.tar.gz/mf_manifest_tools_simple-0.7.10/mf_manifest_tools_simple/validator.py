from mf_manifest_tools_simple.data_struct import MFManifest
from mf_manifest_tools_simple.exceptions import ValidationError


class ManifestValidator(object):
    @staticmethod
    def validate(data: MFManifest):
        ret = []
        datatype_set = set()
        for datatype in data.datatypes:
            if datatype.name in datatype_set:
                ret.append("Datatype {} duplicated".format(datatype.name))
            else:
                datatype_set.add(datatype.name)
            if len(datatype.c_ref.struct.split("::")) != 2:
                ret.append("Datatype {} C reference struct not valid".format(datatype.name))
        topic_set = set()
        for topic in data.topics:
            if topic.datatype not in datatype_set:
                ret.append("Topic {} invalid, datatype {} not exists".format(topic.topic_name, topic.datatype))
            if topic.topic_name in topic_set:
                ret.append("Topic {} duplicated".format(topic.topic_name))
            else:
                topic_set.add(topic.topic_name)
        swc_set = set()
        for swc in data.swcs:
            if swc.name in swc_set:
                ret.append("SWC {} duplicated".format(swc.name))
            else:
                swc_set.add(swc.name)
            sub_port_set = set()
            for sub_port in swc.sub_ports:
                if sub_port.topic_name not in topic_set:
                    ret.append("SWC {} sub port topic {} not exists".format(swc.name, sub_port.topic_name))
                if sub_port.topic_name in sub_port_set:
                    ret.append("SWC {} sub port topic {} duplicated".format(swc.name, sub_port.topic_name))
                else:
                    sub_port_set.add(sub_port.topic_name)
            pub_port_set = set()
            for pub_port in swc.pub_ports:
                if pub_port.topic_name not in topic_set:
                    ret.append("SWC {} pub port topic {} not exists".format(swc.name, pub_port.topic_name))
                if pub_port.topic_name in pub_port_set:
                    ret.append("SWC {} pub port topic {} duplicated".format(swc.name, pub_port.topic_name))
                else:
                    pub_port_set.add(pub_port.topic_name)
        swc_comp_set = set()
        for complementary in data.complementaries:
            if complementary.name in swc_comp_set:
                ret.append("Complementary for SWC {} is duplicated".format(complementary.name))
            else:
                swc_comp_set.add(complementary.name)
            swc = data.filter_swc(complementary.name)
            if swc is None:
                ret.append("SWC {} not found".format(complementary.name))
        if ret:
            raise ValidationError(ret)
