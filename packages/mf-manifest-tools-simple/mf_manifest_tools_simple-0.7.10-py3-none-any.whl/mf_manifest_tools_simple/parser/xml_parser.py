from loguru import logger
from lxml import etree

from mf_manifest_tools_simple.data_struct import *
from mf_manifest_tools_simple.exceptions import *

__all__ = ["ManifestXMLParser"]


class ManifestXMLParser(object):
    def __init__(self, filename: str):
        logger.info("Parsing {}", filename)
        self._parser = etree.XMLParser(dtd_validation=True)
        self._xml = etree.parse(filename, self._parser)
        self._platforms = ["X86", "HUAWEI-MDC"]
        if self._xml.getroot().tag != "MF-PACKAGE":
            raise NotMFManifest()

    def parse_to_db(self, data: MFManifest):
        xml_datatypes = self._xml.xpath("/MF-PACKAGE/MF-DATATYPE")
        for xml_datatype in xml_datatypes:
            if not xml_datatype.attrib["NAME"]:
                raise ManifestNotValid("Datatype name should not be empty")
            datatype = MFDataType(name=xml_datatype.attrib["NAME"])
            if xml_datatype.attrib.has_key("FRAG-SIZE") and xml_datatype.attrib.has_key("LIST-SIZE"):
                try:
                    datatype.frag_size = int(xml_datatype.attrib["FRAG-SIZE"])
                    datatype.list_size = int(xml_datatype.attrib["LIST-SIZE"])
                    if datatype.frag_size <= 0 or datatype.list_size <= 0:
                        raise ValueError()
                except ValueError:
                    datatype.frag_size = -1
                    datatype.list_size = -1
                    raise ManifestNotValid("Datatype {} frag/list size invalid".format(datatype.name))
            xml_datatype_c_ref = xml_datatype.xpath("./MF-DATATYPE-C-REF")
            if xml_datatype_c_ref:
                # TODO: validate, file exists, struct exists
                datatype.c_ref = MFDataTypeCRef(True, xml_datatype_c_ref[0].attrib["FILE"],
                                                xml_datatype_c_ref[0].attrib["STRUCT"])
            xml_datatype_ros_ref = xml_datatype.xpath("./MF-DATATYPE-ROS-REF")
            if xml_datatype_ros_ref:
                # TODO: validate, package exists, struct exists
                datatype.ros_ref = MFDataTypeROSRef(True, xml_datatype_ros_ref[0].attrib["PACKAGE"],
                                                    xml_datatype_ros_ref[0].attrib["STRUCT"])
            xml_datatype_huawei_ref = xml_datatype.xpath("./MF-DATATYPE-HUAWEI-REF")
            if xml_datatype_huawei_ref:
                datatype.huawei_ref = MFDataTypeHuaweiRef(int(xml_datatype_huawei_ref[0].attrib["INTERFACE-ID"]))
                logger.warning("Specifying service interface id on {} is deprecated.", datatype.name)

            if datatype.c_ref.available:
                for dt in data.datatypes:
                    if dt.c_ref.available and dt.c_ref.file == datatype.c_ref.file and dt.c_ref.struct == datatype.c_ref.struct:
                        logger.warning("Datatype {} and {} seems to be the same", datatype.name, dt.name)
            data.datatypes.append(datatype)

        xml_topics = self._xml.xpath("/MF-PACKAGE/MF-TOPIC")
        for xml_topic in xml_topics:
            if not xml_topic.attrib["TOPIC-NAME"]:
                raise ManifestNotValid("Topic name should not be empty")
            topic = MFTopic(topic_name=xml_topic.attrib["TOPIC-NAME"], datatype=xml_topic.attrib["DATATYPE"])
            xml_topic_ros_ref = xml_topic.xpath("./MF-TOPIC-ROS-REF")
            if xml_topic_ros_ref:
                if not xml_topic_ros_ref[0].attrib["ROS-TOPIC"]:
                    raise ManifestNotValid("ROS topic should not be empty")
                topic.ros_ref = MFTopicROSRef(True, xml_topic_ros_ref[0].attrib["ROS-TOPIC"])
            xml_topic_mfr_ref = xml_topic.xpath("./MF-TOPIC-MFR-REF")
            if xml_topic_mfr_ref:
                if not xml_topic_mfr_ref[0].attrib["MFR-TOPIC"]:
                    raise ManifestNotValid("MFR topic should not be empty")
                topic.mfr_ref = MFTopicMFRRef(True, xml_topic_mfr_ref[0].attrib["MFR-TOPIC"])
            xml_topic_motionwise_ref = xml_topic.xpath("./MF-TOPIC-MOTIONWISE-REF")
            if xml_topic_motionwise_ref:
                if xml_topic_motionwise_ref[0].attrib.has_key("RTE"):
                    topic.motionwise_ref.rte = xml_topic_motionwise_ref[0].attrib["RTE"]
            xml_topic_huawei_ref = xml_topic.xpath("./MF-TOPIC-HUAWEI-REF")
            if xml_topic_huawei_ref:
                if xml_topic_huawei_ref[0].attrib.has_key("USE-SOMEIP"):
                    topic.huawei_ref.is_someip = (xml_topic_huawei_ref[0].attrib["USE-SOMEIP"] == "TRUE")
            platform = []
            if not xml_topic.attrib.has_key("PLATFORM") or xml_topic.attrib["PLATFORM"] == "ALL":
                # All
                platform = self._platforms
            else:
                xml_platforms = xml_topic.attrib["PLATFORM"].split(",")
                for p in xml_platforms:
                    if p not in self._platforms:
                        raise ManifestNotValid("Topic {} platform not valid".format(topic.topic_name))
                    else:
                        platform.append(p)
            topic.platforms = platform
            data.topics.append(topic)

        xml_swcs = self._xml.xpath("/MF-PACKAGE/MF-SWC")
        for xml_swc in xml_swcs:
            if not xml_swc.attrib["NAME"]:
                raise ManifestNotValid("SWC name should not be empty")
            swc = MFSWC(name=xml_swc.attrib["NAME"])
            if xml_swc.attrib.has_key("GROUP"):
                swc.group = xml_swc.attrib["GROUP"]
            huawei_ref = xml_swc.xpath("./MF-SWC-HUAWEI-REF")
            if huawei_ref:
                if huawei_ref[0].attrib.has_key("IS-IN-AOS-CORE"):
                    swc.huawei_ref.is_in_aos_core = (huawei_ref[0].attrib["IS-IN-AOS-CORE"] == "TRUE")
            # Sub ports
            xml_sub_ports = xml_swc.xpath("./MF-SUB-PORTS/MF-PORT")
            for xml_sub_port in xml_sub_ports:
                if not xml_sub_port.attrib["TOPIC-NAME"]:
                    raise ManifestNotValid("SUB topic name should not be empty")
                swc.sub_ports.append(MFPort(topic_name=xml_sub_port.attrib["TOPIC-NAME"]))
            # Sub huawei ports
            xml_sub_huawei_ports = xml_swc.xpath("./MF-SUB-PORTS/MF-PORT-HUAWEI-REF")
            for xml_sub_huawei_port in xml_sub_huawei_ports:
                if not xml_sub_huawei_port.attrib["DATATYPE-NAME"] or not xml_sub_huawei_port.attrib[
                    "SERVICE-INTERFACE"] or not xml_sub_huawei_port.attrib["INSTANCE-ID"] or not \
                        xml_sub_huawei_port.attrib["TRANSPORT-PLUGIN"] or not xml_sub_huawei_port.attrib[
                    "SERVICE-INTERFACE-DEPLOYMENT"] or not xml_sub_huawei_port.attrib["EVENT-DEPLOYMENT"] or not \
                        xml_sub_huawei_port.attrib["DOMAIN-ID"]:
                    raise ManifestNotValid("SWC {} sub huawei port ref not valid".format(swc.name))
                swc.sub_huawei_ports.append(MFPortHuaweiRef(datatype_name=xml_sub_huawei_port.attrib["DATATYPE-NAME"],
                                                            service_interface=xml_sub_huawei_port.attrib[
                                                                "SERVICE-INTERFACE"],
                                                            instance_id=xml_sub_huawei_port.attrib["INSTANCE-ID"],
                                                            transport_plugin=xml_sub_huawei_port.attrib[
                                                                "TRANSPORT-PLUGIN"],
                                                            service_interface_deployment=xml_sub_huawei_port.attrib[
                                                                "SERVICE-INTERFACE-DEPLOYMENT"],
                                                            event_deployment=xml_sub_huawei_port.attrib[
                                                                "EVENT-DEPLOYMENT"],
                                                            domain_id=int(xml_sub_huawei_port.attrib["DOMAIN-ID"])))
            # Pub ports
            xml_pub_ports = xml_swc.xpath("./MF-PUB-PORTS/MF-PORT")
            for xml_pub_port in xml_pub_ports:
                if not xml_pub_port.attrib["TOPIC-NAME"]:
                    raise ManifestNotValid("PUB topic name should not be empty")
                swc.pub_ports.append(MFPort(topic_name=xml_pub_port.attrib["TOPIC-NAME"]))
            # Pub huawei ports
            xml_pub_huawei_ports = xml_swc.xpath("./MF-PUB-PORTS/MF-PORT-HUAWEI-REF")
            for xml_pub_huawei_port in xml_pub_huawei_ports:
                if not xml_pub_huawei_port.attrib["DATATYPE-NAME"] or not xml_pub_huawei_port.attrib[
                    "SERVICE-INTERFACE"] or not xml_pub_huawei_port.attrib["INSTANCE-ID"] or not \
                        xml_pub_huawei_port.attrib["TRANSPORT-PLUGIN"] or not xml_pub_huawei_port.attrib[
                    "SERVICE-INTERFACE-DEPLOYMENT"] or not xml_pub_huawei_port.attrib["EVENT-DEPLOYMENT"] or not \
                        xml_pub_huawei_port.attrib["DOMAIN-ID"]:
                    raise ManifestNotValid("SWC {} pub huawei port ref not valid".format(swc.name))
                swc.pub_huawei_ports.append(MFPortHuaweiRef(datatype_name=xml_pub_huawei_port.attrib["DATATYPE-NAME"],
                                                            service_interface=xml_pub_huawei_port.attrib[
                                                                "SERVICE-INTERFACE"],
                                                            instance_id=xml_pub_huawei_port.attrib["INSTANCE-ID"],
                                                            transport_plugin=xml_pub_huawei_port.attrib[
                                                                "TRANSPORT-PLUGIN"],
                                                            service_interface_deployment=xml_pub_huawei_port.attrib[
                                                                "SERVICE-INTERFACE-DEPLOYMENT"],
                                                            event_deployment=xml_pub_huawei_port.attrib[
                                                                "EVENT-DEPLOYMENT"],
                                                            domain_id=int(xml_pub_huawei_port.attrib["DOMAIN-ID"])))
            # function description
            tmp = xml_swc.xpath('./MF-SWC-FUNCTION-DESC')
            if tmp:
                swc.function_description = xml_swc.xpath('./MF-SWC-FUNCTION-DESC')[0].text
            tmp = xml_swc.xpath('./MF-SWC-CPU-USAGE')
            if tmp:
                swc.cpu_usage = xml_swc.xpath('./MF-SWC-CPU-USAGE')[0].text
            tmp = xml_swc.xpath('./MF-SWC-MEMORY-USAGE')
            if tmp:
                swc.memory_usage = xml_swc.xpath('./MF-SWC-MEMORY-USAGE')[0].text
            data.swcs.append(swc)

        xml_complementaries = self._xml.xpath("/MF-PACKAGE/MF-COMPLEMENTARY")
        for xml_complementary in xml_complementaries:
            if not xml_complementary.attrib["NAME"]:
                raise ManifestNotValid("SWC name should not be empty")
            cp = MFComplementary(name=xml_complementary.attrib["NAME"])
            cp.api_period = xml_complementary.xpath("./API-PERIOD")[0].text
            cp.logic_convert_function = xml_complementary.xpath("./LOGIC-CONVERT-FUNCTION")[0].text
            cp.api_normal_description = xml_complementary.xpath("./API-NORMAL-DESCRIPTION")[0].text
            cp.api_abnormal_description = xml_complementary.xpath("./API-ABNORMAL-DESCRIPTION")[0].text
            cp.function_work = xml_complementary.xpath("./FUNCTION-WORK")[0].text
            cp.logic_function = xml_complementary.xpath("./LOGIC-FUNCTION")[0].text
            for inp in xml_complementary.xpath("./INPUTS/INPUT"):
                cp.inputs.append(inp.text)
            for oup in xml_complementary.xpath("./OUTPUTS/OUTPUT"):
                cp.outputs.append(oup.text)
            for ret in xml_complementary.xpath("./RETURNS/RETURN"):
                cp.returns.append(ret.text)
            cp.last_return = xml_complementary.xpath("./LAST-RETURN")[0].text
            data.complementaries.append(cp)
