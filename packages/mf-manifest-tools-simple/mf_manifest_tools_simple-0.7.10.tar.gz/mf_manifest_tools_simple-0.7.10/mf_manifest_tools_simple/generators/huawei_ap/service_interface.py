from inflection import underscore
from loguru import logger
from lxml import etree

from mf_manifest_tools_simple.data_struct import MFManifest, MFDataType
from mf_manifest_tools_simple.generators.huawei_ap.common import set_short_name, generate_empty_arxml

__all__ = ["HuaweiAPServiceInterfaceGenerator"]


class HuaweiAPServiceInterfaceGenerator(object):
    @staticmethod
    def _generate_one_datatype_dds(datatype: MFDataType, elements: etree.Element):
        # SERVICE-INTERFACE
        node = etree.SubElement(elements, "SERVICE-INTERFACE")
        set_short_name(node, datatype.name + "ServiceInterface")
        is_service = etree.SubElement(node, "IS-SERVICE")
        is_service.text = "true"
        namespaces = etree.SubElement(node, "NAMESPACES")
        struct_name = datatype.c_ref.struct.split("::")
        ns = etree.Element("SYMBOL-PROPS")
        set_short_name(ns, "ap_" + struct_name[0])
        ns_symbol = etree.SubElement(ns, "SYMBOL")
        ns_symbol.text = "ap_" + struct_name[0]
        ns1 = etree.Element("SYMBOL-PROPS")
        set_short_name(ns1, underscore(struct_name[1]) + "_service_interface")
        ns_symbol1 = etree.SubElement(ns1, "SYMBOL")
        ns_symbol1.text = underscore(struct_name[1]) + "_service_interface"
        namespaces.append(ns)
        namespaces.append(ns1)
        events = etree.SubElement(node, "EVENTS")
        prototype = etree.SubElement(events, "VARIABLE-DATA-PROTOTYPE")
        set_short_name(prototype, "mdcEvent")
        type_ref = etree.SubElement(prototype, "TYPE-TREF")
        type_ref.attrib["DEST"] = "STD-CPP-IMPLEMENTATION-DATA-TYPE"
        type_ref.text = "/ai/momenta/data_type/" + "/".join(struct_name)

        # DDS-SERVICE-INTERFACE-DEPLOYMENT
        deployment = etree.SubElement(elements, "DDS-SERVICE-INTERFACE-DEPLOYMENT")
        set_short_name(deployment, datatype.name + "ServiceInterfaceDeployment")
        event_deployments = etree.SubElement(deployment, "EVENT-DEPLOYMENTS")
        dds_deployment = etree.SubElement(event_deployments, "DDS-EVENT-DEPLOYMENT")
        set_short_name(dds_deployment, datatype.name + "DdsEventDeployment")
        event_ref = etree.SubElement(dds_deployment, "EVENT-REF")
        event_ref.attrib["DEST"] = "VARIABLE-DATA-PROTOTYPE"
        event_ref.text = "/ai/momenta/service_interface/" + datatype.name + "ServiceInterface/mdcEvent"
        topic_name = etree.SubElement(dds_deployment, "TOPIC-NAME")
        topic_name.text = datatype.name + "DdsEvent"
        transport_protocols = etree.SubElement(dds_deployment, "TRANSPORT-PROTOCOLS")
        transport_protocol = etree.SubElement(transport_protocols, "TRANSPORT-PROTOCOL")
        transport_protocol.text = "UDP"

        if datatype.list_size > 0 and datatype.frag_size > 0:
            frag_size = etree.SubElement(dds_deployment, "FRAG-SIZE")
            frag_size.text = str(datatype.frag_size)
            list_size = etree.SubElement(dds_deployment, "LIST-SIZE")
            list_size.text = str(datatype.list_size)
        interface_ref = etree.SubElement(deployment, "SERVICE-INTERFACE-REF")
        interface_ref.attrib["DEST"] = "SERVICE-INTERFACE"
        interface_ref.text = "/ai/momenta/service_interface/" + datatype.name + "ServiceInterface"
        interface_id = etree.SubElement(deployment, "SERVICE-INTERFACE-ID")
        interface_id.text = str(datatype.huawei_ref.interface_id)

    @staticmethod
    def _generate_one_datatype_someip(datatype: MFDataType, elements: etree.Element):
        # SERVICE-INTERFACE
        node = etree.SubElement(elements, "SERVICE-INTERFACE")
        set_short_name(node, datatype.name + "ServiceInterfaceSomeIp")
        is_service = etree.SubElement(node, "IS-SERVICE")
        is_service.text = "true"
        namespaces = etree.SubElement(node, "NAMESPACES")
        struct_name = datatype.c_ref.struct.split("::")
        ns = etree.Element("SYMBOL-PROPS")
        set_short_name(ns, "ap_" + struct_name[0])
        ns_symbol = etree.SubElement(ns, "SYMBOL")
        ns_symbol.text = "ap_" + struct_name[0]
        ns1 = etree.Element("SYMBOL-PROPS")
        set_short_name(ns1, underscore(struct_name[1]) + "_service_interface_someip")
        ns_symbol1 = etree.SubElement(ns1, "SYMBOL")
        ns_symbol1.text = underscore(struct_name[1]) + "_service_interface_someip"
        namespaces.append(ns)
        namespaces.append(ns1)
        events = etree.SubElement(node, "EVENTS")
        prototype = etree.SubElement(events, "VARIABLE-DATA-PROTOTYPE")
        set_short_name(prototype, "mdcEvent")
        type_ref = etree.SubElement(prototype, "TYPE-TREF")
        type_ref.attrib["DEST"] = "STD-CPP-IMPLEMENTATION-DATA-TYPE"
        type_ref.text = "/ai/momenta/data_type/" + "/".join(struct_name)

        # DDS-SERVICE-INTERFACE-DEPLOYMENT
        deployment = etree.SubElement(elements, "SOMEIP-SERVICE-INTERFACE-DEPLOYMENT")
        set_short_name(deployment, datatype.name + "ServiceInterfaceSomeIpDeployment")
        event_deployments = etree.SubElement(deployment, "EVENT-DEPLOYMENTS")
        someip_deployment = etree.SubElement(event_deployments, "SOMEIP-EVENT-DEPLOYMENT")
        set_short_name(someip_deployment, datatype.name + "SomeIpEventDeployment")
        event_ref = etree.SubElement(someip_deployment, "EVENT-REF")
        event_ref.attrib["DEST"] = "VARIABLE-DATA-PROTOTYPE"
        event_ref.text = "/ai/momenta/service_interface/" + datatype.name + "ServiceInterfaceSomeIp/mdcEvent"
        event_id = etree.SubElement(someip_deployment, "EVENT-ID")
        event_id.text = "1"
        transport_protocol = etree.SubElement(someip_deployment, "TRANSPORT-PROTOCOL")
        transport_protocol.text = "UDP"
        interface_ref = etree.SubElement(deployment, "SERVICE-INTERFACE-REF")
        interface_ref.attrib["DEST"] = "SERVICE-INTERFACE"
        interface_ref.text = "/ai/momenta/service_interface/" + datatype.name + "ServiceInterfaceSomeIp"
        event_groups = etree.SubElement(deployment, "EVENT-GROUPS")
        someip_event_group = etree.SubElement(event_groups, "SOMEIP-EVENT-GROUP")
        set_short_name(someip_event_group, datatype.name + "SomeIpEventGroup")
        event_group_id = etree.SubElement(someip_event_group, "EVENT-GROUP-ID")
        event_group_id.text = "1"
        group_event_refs = etree.SubElement(someip_event_group, "EVENT-REFS")
        group_event_ref = etree.SubElement(group_event_refs, "EVENT-REF")
        group_event_ref.attrib["DEST"] = "SOMEIP-EVENT-DEPLOYMENT"
        group_event_ref.text = "/ai/momenta/service_interface/" + datatype.name + "ServiceInterfaceSomeIpDeployment/" + datatype.name + "SomeIpEventDeployment"
        interface_id = etree.SubElement(deployment, "SERVICE-INTERFACE-ID")
        # Hacking, offset 1e5
        interface_id.text = str(int(10000 + datatype.huawei_ref.interface_id))
        interface_version = etree.SubElement(deployment, "SERVICE-INTERFACE-VERSION")
        major_version = etree.SubElement(interface_version, "MAJOR-VERSION")
        major_version.text = "1"
        minor_version = etree.SubElement(interface_version, "MINOR-VERSION")
        minor_version.text = "1"

    @staticmethod
    def _get_datatype_channel(datatype: MFDataType, data: MFManifest):
        has_dds = False
        has_someip = False
        for topic in data.topics:
            if topic.datatype == datatype.name:
                if topic.huawei_ref.is_someip:
                    has_someip = True
                else:
                    has_dds = True
                if has_dds and has_someip:
                    return "both"
        if has_dds:
            return "dds"
        return "someip"

    @staticmethod
    def generate(data: MFManifest):
        doc, ar_package_momenta = generate_empty_arxml()
        ar_package_momenta_packages = etree.SubElement(ar_package_momenta, "AR-PACKAGES")
        ar_package_service_interface = etree.SubElement(ar_package_momenta_packages, "AR-PACKAGE")
        set_short_name(ar_package_service_interface, "service_interface")
        elements = etree.SubElement(ar_package_service_interface, "ELEMENTS")

        for datatype in data.datatypes:
            if data.is_datatype_referenced(datatype.name):
                channel = HuaweiAPServiceInterfaceGenerator._get_datatype_channel(datatype, data)
                if channel in ["dds", "both"]:
                    HuaweiAPServiceInterfaceGenerator._generate_one_datatype_dds(datatype, elements)
                if channel in ["someip", "both"]:
                    HuaweiAPServiceInterfaceGenerator._generate_one_datatype_someip(datatype, elements)
            else:
                logger.warning("Datatype {} is never used", datatype.name)

        return etree.tostring(doc, xml_declaration=True, encoding="UTF-8", pretty_print=True)
