from lxml import etree

from mf_manifest_tools_simple.data_struct import MFManifest, MFServiceInstance, MFPortHuaweiRef, MFSWC
from mf_manifest_tools_simple.generators.huawei_ap.common import set_short_name, generate_empty_arxml

__all__ = ["HuaweiAPServiceInstanceGenerator"]


class HuaweiAPServiceInstanceGenerator(object):
    udp_port_num = 61000

    @staticmethod
    def _element_single_service_instance_huawei(port: MFPortHuaweiRef, is_provided: bool, swc: MFSWC, elements,
                                                machine: str):
        dt_name = port.datatype_name.split("::")[-1]
        # DDS-PROVIDED-SERVICE-INSTANCE
        _instance = etree.SubElement(elements,
                                     "DDS-PROVIDED-SERVICE-INSTANCE" if is_provided else "DDS-REQUIRED-SERVICE-INSTANCE")
        set_short_name(_instance,
                       dt_name + port.instance_id + (
                           "ProvidedInstanceBy" + swc.name if is_provided else "RequiredInstanceByHuawei"))
        deployment = etree.SubElement(_instance, "SERVICE-INTERFACE-DEPLOYMENT-REF")
        deployment.attrib["DEST"] = "DDS-SERVICE-INTERFACE-DEPLOYMENT"
        deployment.text = port.service_interface_deployment
        qos_profile = etree.SubElement(_instance, "QOS-PROFILE")
        qos_profile.text = "/var/domainqos.xml"
        domain_id = etree.SubElement(_instance, "DOMAIN-ID")
        domain_id.text = str(port.domain_id)
        transport_plugins = etree.SubElement(_instance, "TRANSPORT-PLUGINS")
        for plugin in port.transport_plugin.split("+"):
            transport_plugin = etree.SubElement(transport_plugins, "TRANSPORT-PLUGIN")
            transport_plugin.text = plugin
        event_qos_propss = etree.SubElement(_instance, "EVENT-QOS-PROPSS")
        dds_qos_props = etree.SubElement(event_qos_propss, "DDS-EVENT-QOS-PROPS")
        event_ref = etree.SubElement(dds_qos_props, "EVENT-REF")
        event_ref.attrib["DEST"] = "DDS-EVENT-DEPLOYMENT"
        event_ref.text = port.event_deployment
        xml_instance_id = etree.SubElement(_instance,
                                           "SERVICE-INSTANCE-ID" if is_provided else "REQUIRED-SERVICE-INSTANCE-ID")
        xml_instance_id.text = port.instance_id

        # DDS-SERVICE-INSTANCE-TO-MACHINE-MAPPING
        _instance_mapping = etree.SubElement(elements, "DDS-SERVICE-INSTANCE-TO-MACHINE-MAPPING")
        set_short_name(_instance_mapping,
                       dt_name + port.instance_id + (
                           "Provided" if is_provided else "Required") + "InstanceMapping")
        _connector_ref = etree.SubElement(_instance_mapping, "COMMUNICATION-CONNECTOR-REF")
        _connector_ref.attrib["DEST"] = "ETHERNET-COMMUNICATION-CONNECTOR"
        _connector_ref.text = "/HuaweiMDC/{machine}Machine/{machine}MachineDesign/InnerEthernetCommConnector".format(
            machine=machine)
        _instance_refs = etree.SubElement(_instance_mapping, "SERVICE-INSTANCE-REFS")
        _instance_ref = etree.SubElement(_instance_refs, "SERVICE-INSTANCE-REF")
        _instance_ref.attrib[
            "DEST"] = "DDS-PROVIDED-SERVICE-INSTANCE" if is_provided else "DDS-REQUIRED-SERVICE-INSTANCE"
        _instance_ref.text = "/ai/momenta/service_instance/" + dt_name + port.instance_id + (
            "ProvidedInstanceBy" + swc.name if is_provided else "RequiredInstanceByHuawei")

    @staticmethod
    def _element_single_service_instance_someip(instance: MFServiceInstance, is_provided: bool, elements, machine: str):
        _instance = etree.SubElement(elements,
                                     "PROVIDED-SOMEIP-SERVICE-INSTANCE" if is_provided else "REQUIRED-SOMEIP-SERVICE-INSTANCE")
        set_short_name(_instance,
                       instance.datatype.name + str(instance.instance_id) + (
                           "Provided" if is_provided else "Required") +
                       "InstanceBy" + instance.sender_swc.name + "SomeIp")
        deployment = etree.SubElement(_instance, "SERVICE-INTERFACE-DEPLOYMENT-REF")
        deployment.attrib["DEST"] = "SOMEIP-SERVICE-INTERFACE-DEPLOYMENT"
        deployment.text = "/ai/momenta/service_interface/" + instance.datatype.name + "ServiceInterfaceSomeIpDeployment"
        xml_instance_id = etree.SubElement(_instance,
                                           "SERVICE-INSTANCE-ID" if is_provided else "REQUIRED-SERVICE-INSTANCE-ID")
        xml_instance_id.text = str(instance.instance_id)
        if is_provided:
            sd_client_config_ref = etree.SubElement(_instance, "SD-SERVER-CONFIG-REF")
            sd_client_config_ref.attrib["DEST"] = "SOMEIP-SD-SERVER-SERVICE-INSTANCE-CONFIG"
            sd_client_config_ref.text = "/HuaweiMDC/SomeipSdConfig/{machine}SomeipSdServerServiceInstanceConfig".format(
                machine=machine)
        else:
            sd_client_config_ref = etree.SubElement(_instance, "SD-CLIENT-CONFIG-REF")
            sd_client_config_ref.attrib["DEST"] = "SOMEIP-SD-CLIENT-SERVICE-INSTANCE-CONFIG"
            sd_client_config_ref.text = "/HuaweiMDC/SomeipSdConfig/{machine}SomeipSdClientServiceInstanceConfig".format(
                machine=machine)

        _instance_mapping = etree.SubElement(elements, "SOMEIP-SERVICE-INSTANCE-TO-MACHINE-MAPPING")
        set_short_name(_instance_mapping,
                       instance.datatype.name + str(
                           instance.instance_id) + (
                           "Provided" if is_provided else "Required") + "InstanceMappingSomeIp")
        _connector_ref = etree.SubElement(_instance_mapping, "COMMUNICATION-CONNECTOR-REF")
        _connector_ref.attrib["DEST"] = "ETHERNET-COMMUNICATION-CONNECTOR"
        _connector_ref.text = "/HuaweiMDC/{machine}Machine/{machine}MachineDesign/InnerEthernetCommConnector".format(
            machine=machine)
        _instance_refs = etree.SubElement(_instance_mapping, "SERVICE-INSTANCE-REFS")
        _instance_ref = etree.SubElement(_instance_refs, "SERVICE-INSTANCE-REF")
        _instance_ref.attrib[
            "DEST"] = "PROVIDED-SOMEIP-SERVICE-INSTANCE" if is_provided else "REQUIRED-SOMEIP-SERVICE-INSTANCE"
        _instance_ref.text = "/ai/momenta/service_instance/" + instance.datatype.name + str(
            instance.instance_id) + (
                                 "Provided" if is_provided else "Required") + "InstanceBy" + instance.sender_swc.name + "SomeIp"
        udp_port = etree.SubElement(_instance_mapping, "UDP-PORT")
        udp_port.text = str(HuaweiAPServiceInstanceGenerator.udp_port_num)

    @staticmethod
    def _element_single_service_instance_dds(instance: MFServiceInstance, is_provided: bool, elements, machine: str,
                                             is_in_aos_core: bool = False, is_cross_domain=False):
        # DDS-PROVIDED-SERVICE-INSTANCE
        _instance = etree.SubElement(elements,
                                     "DDS-PROVIDED-SERVICE-INSTANCE" if is_provided else "DDS-REQUIRED-SERVICE-INSTANCE")
        set_short_name(_instance,
                       instance.datatype.name + str(instance.instance_id) + (
                           "Provided" if is_provided else "Required") +
                       "InstanceBy" + instance.sender_swc.name + ("ICC" if is_in_aos_core else ""))
        deployment = etree.SubElement(_instance, "SERVICE-INTERFACE-DEPLOYMENT-REF")
        deployment.attrib["DEST"] = "DDS-SERVICE-INTERFACE-DEPLOYMENT"
        deployment.text = "/ai/momenta/service_interface/" + instance.datatype.name + "ServiceInterfaceDeployment"
        qos_profile = etree.SubElement(_instance, "QOS-PROFILE")
        qos_profile.text = "/var/domainqos.xml"
        domain_id = etree.SubElement(_instance, "DOMAIN-ID")
        domain_id.text = str(instance.topic.huawei_ref.domain_id)
        transport_plugins = etree.SubElement(_instance, "TRANSPORT-PLUGINS")
        if is_provided:
            if is_cross_domain:
                transport_plugin_1 = etree.SubElement(transport_plugins, "TRANSPORT-PLUGIN")
                transport_plugin_1.text = "ICC"
            if instance.datatype.frag_size > 0 and instance.datatype.list_size > 0:
                transport_plugin_2 = etree.SubElement(transport_plugins, "TRANSPORT-PLUGIN")
                transport_plugin_2.text = "SHM"
            else:
                transport_plugin_2 = etree.SubElement(transport_plugins, "TRANSPORT-PLUGIN")
                transport_plugin_2.text = "DSHM"
        elif is_in_aos_core:
            transport_plugin = etree.SubElement(transport_plugins, "TRANSPORT-PLUGIN")
            transport_plugin.text = "ICC"
        else:
            if instance.datatype.frag_size > 0 and instance.datatype.list_size > 0:
                transport_plugin = etree.SubElement(transport_plugins, "TRANSPORT-PLUGIN")
                transport_plugin.text = "SHM"
            else:
                transport_plugin = etree.SubElement(transport_plugins, "TRANSPORT-PLUGIN")
                transport_plugin.text = "DSHM"
        event_qos_propss = etree.SubElement(_instance, "EVENT-QOS-PROPSS")
        dds_qos_props = etree.SubElement(event_qos_propss, "DDS-EVENT-QOS-PROPS")
        event_ref = etree.SubElement(dds_qos_props, "EVENT-REF")
        event_ref.attrib["DEST"] = "DDS-EVENT-DEPLOYMENT"
        event_ref.text = "/ai/momenta/service_interface/" + instance.datatype.name + "ServiceInterfaceDeployment/" + \
                         instance.datatype.name + "DdsEventDeployment"
        xml_instance_id = etree.SubElement(_instance,
                                           "SERVICE-INSTANCE-ID" if is_provided else "REQUIRED-SERVICE-INSTANCE-ID")
        xml_instance_id.text = str(instance.instance_id)

        # DDS-SERVICE-INSTANCE-TO-MACHINE-MAPPING
        _instance_mapping = etree.SubElement(elements, "DDS-SERVICE-INSTANCE-TO-MACHINE-MAPPING")
        set_short_name(_instance_mapping,
                       instance.datatype.name + str(
                           instance.instance_id) + ("Provided" if is_provided else "Required") + "InstanceMapping" + (
                           "ICC" if is_in_aos_core else ""))
        _connector_ref = etree.SubElement(_instance_mapping, "COMMUNICATION-CONNECTOR-REF")
        _connector_ref.attrib["DEST"] = "ETHERNET-COMMUNICATION-CONNECTOR"
        _connector_ref.text = "/HuaweiMDC/{machine}Machine/{machine}MachineDesign/InnerEthernetCommConnector".format(
            machine=machine)
        _instance_refs = etree.SubElement(_instance_mapping, "SERVICE-INSTANCE-REFS")
        _instance_ref = etree.SubElement(_instance_refs, "SERVICE-INSTANCE-REF")
        _instance_ref.attrib[
            "DEST"] = "DDS-PROVIDED-SERVICE-INSTANCE" if is_provided else "DDS-REQUIRED-SERVICE-INSTANCE"
        _instance_ref.text = "/ai/momenta/service_instance/" + instance.datatype.name + str(
            instance.instance_id) + (
                                 "Provided" if is_provided else "Required") + "InstanceBy" + instance.sender_swc.name + (
                                 "ICC" if is_in_aos_core else "")

    @staticmethod
    def is_provided_instance_cross_domain(instance: MFServiceInstance, data: MFManifest):
        connections = list(filter(lambda x: x.instance == instance, data.connections))
        for conn in connections:
            if conn.sender_swc.huawei_ref.is_in_aos_core != conn.receiver_swc.huawei_ref.is_in_aos_core:
                return True
        return False

    @staticmethod
    def generate(data: MFManifest, machine: str):
        doc, ar_package_momenta = generate_empty_arxml()
        ar_package_momenta_packages = etree.SubElement(ar_package_momenta, "AR-PACKAGES")
        ar_package_service_instance = etree.SubElement(ar_package_momenta_packages, "AR-PACKAGE")
        short_name_3 = etree.SubElement(ar_package_service_instance, "SHORT-NAME")
        short_name_3.text = "service_instance"
        elements = etree.SubElement(ar_package_service_instance, "ELEMENTS")

        for instance in data.service_instances:
            if "HUAWEI-MDC" in instance.topic.platforms:
                if instance.topic.huawei_ref.is_someip:
                    HuaweiAPServiceInstanceGenerator._element_single_service_instance_someip(instance, is_provided=True,
                                                                                             elements=elements,
                                                                                             machine=machine)
                    HuaweiAPServiceInstanceGenerator._element_single_service_instance_someip(instance,
                                                                                             is_provided=False,
                                                                                             elements=elements,
                                                                                             machine=machine)
                    HuaweiAPServiceInstanceGenerator.udp_port_num += 1
                else:
                    is_cross_domain = HuaweiAPServiceInstanceGenerator.is_provided_instance_cross_domain(instance, data)
                    # Provided instance
                    HuaweiAPServiceInstanceGenerator._element_single_service_instance_dds(instance, is_provided=True,
                                                                                          elements=elements,
                                                                                          machine=machine,
                                                                                          is_cross_domain=is_cross_domain)
                    # Required instance
                    HuaweiAPServiceInstanceGenerator._element_single_service_instance_dds(instance, is_provided=False,
                                                                                          elements=elements,
                                                                                          machine=machine,
                                                                                          is_cross_domain=is_cross_domain)  # DSHM
                    if is_cross_domain:
                        HuaweiAPServiceInstanceGenerator._element_single_service_instance_dds(instance,
                                                                                              is_provided=False,
                                                                                              elements=elements,
                                                                                              machine=machine,
                                                                                              is_in_aos_core=True,
                                                                                              is_cross_domain=is_cross_domain)  # ICC
        huawei_set = set()
        for swc in data.swcs:
            for sub in swc.sub_huawei_ports:
                key = ("sub", sub.datatype_name, sub.instance_id, sub.transport_plugin, sub.service_interface)
                if key not in huawei_set:
                    HuaweiAPServiceInstanceGenerator._element_single_service_instance_huawei(sub, False, swc, elements,
                                                                                             machine=machine)
                    huawei_set.add(key)
            for pub in swc.pub_huawei_ports:
                key = ("pub", pub.datatype_name, pub.instance_id, pub.transport_plugin, pub.service_interface)
                if key not in huawei_set:
                    HuaweiAPServiceInstanceGenerator._element_single_service_instance_huawei(pub, True, swc, elements,
                                                                                             machine=machine)
                    huawei_set.add(key)
        return etree.tostring(doc, xml_declaration=True, encoding="UTF-8", pretty_print=True)
