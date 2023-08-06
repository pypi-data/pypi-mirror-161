from lxml import etree

from mf_manifest_tools_simple.data_struct import MFManifest, MFSWC
from mf_manifest_tools_simple.generators.huawei_ap.common import set_short_name, generate_empty_arxml

__all__ = ["HuaweiAPSWCGenerator"]


class HuaweiAPSWCGenerator(object):
    sea_base_dir = "/opt/usr/app/1/sea"
    gea_base_dir = "/opt/usr/app/1/gea"

    @staticmethod
    def _generate_em(data: MFManifest, node: etree.Element, machine: str):
        elements = etree.SubElement(node, "ELEMENTS")

        # PROCESS-TO-MACHINE-MAPPING-SET
        process_to_machine_set = etree.SubElement(
            elements, "PROCESS-TO-MACHINE-MAPPING-SET")
        set_short_name(process_to_machine_set, "ProcessToMachineMappingSet")
        mappings = etree.SubElement(
            process_to_machine_set, "PROCESS-TO-MACHINE-MAPPINGS")
        for swc in data.swcs:
            mapping = etree.SubElement(mappings, "PROCESS-TO-MACHINE-MAPPING")
            set_short_name(mapping, swc.name + "ToMachineMapping")
            machine_ref = etree.SubElement(mapping, "MACHINE-REF")
            machine_ref.attrib["DEST"] = "MACHINE"
            machine_ref.text = "/HuaweiMDC/{machine}Machine/{machine}Machine".format(
                machine=machine)
            process_ref = etree.SubElement(mapping, "PROCESS-REF")
            process_ref.attrib["DEST"] = "PROCESS"
            process_ref.text = "/ai/momenta/swc/" + swc.name + "/" + swc.name + "Process"
            if swc.affinitiy:
                shall_run_on_refs = etree.SubElement(
                    mapping, "SHALL-RUN-ON-REFS")
                for core in swc.affinitiy:
                    shall_run_on_ref = etree.SubElement(
                        shall_run_on_refs, "SHALL-RUN-ON-REF")
                    shall_run_on_ref.attrib["DEST"] = "PROCESSOR-CORE"
                    shall_run_on_ref.text = "/HuaweiMDC/{machine}Machine/{machine}Machine/Cpu/Processor0_Core{core}".format(
                        machine=machine, core=core)

        # Startup configs Set
        startup_config_set = etree.SubElement(elements, "STARTUP-CONFIG-SET")
        set_short_name(startup_config_set, "StartupConfigSet")
        configs = etree.SubElement(startup_config_set, "STARTUP-CONFIGS")
        for swc in data.swcs:
            config = etree.SubElement(configs, "STARTUP-CONFIG")
            set_short_name(config, swc.name + "StartupConfig")
            enviroment_variables = etree.SubElement(
                config, "ENVIRONMENT-VARIABLES")
            tag_with_optional_value_1 = etree.SubElement(
                enviroment_variables, "TAG-WITH-OPTIONAL-VALUE")
            key_1 = etree.SubElement(tag_with_optional_value_1, "KEY")
            key_1.text = "LD_LIBRARY_PATH"
            value_1 = etree.SubElement(tag_with_optional_value_1, "VALUE")
            value_1.text = "{base}/lib:{base}/runtime_service/{name}Root/lib".format(
                    base=HuaweiAPSWCGenerator.sea_base_dir if swc.huawei_ref.is_in_aos_core else HuaweiAPSWCGenerator.gea_base_dir,
                    name=swc.name
            )

            tag_with_optional_value_2 = etree.SubElement(
                enviroment_variables, "TAG-WITH-OPTIONAL-VALUE")
            key = etree.SubElement(tag_with_optional_value_2, "KEY")
            key.text = "CM_CONFIG_FILE_PATH"
            value = etree.SubElement(tag_with_optional_value_2, "VALUE")
            value.text = "{base}/runtime_service/{name}Root/etc/{name}Process".format(
                base=HuaweiAPSWCGenerator.sea_base_dir if swc.huawei_ref.is_in_aos_core else HuaweiAPSWCGenerator.gea_base_dir,
                name=swc.name
            )

            tag_with_optional_value_3 = etree.SubElement(
                enviroment_variables, "TAG-WITH-OPTIONAL-VALUE")
            key = etree.SubElement(tag_with_optional_value_3, "KEY")
            key.text = "EXEC_PATH"
            value = etree.SubElement(tag_with_optional_value_3, "VALUE")
            value.text = "{base}/runtime_service/{name}Root/bin".format(
                base=HuaweiAPSWCGenerator.sea_base_dir if swc.huawei_ref.is_in_aos_core else HuaweiAPSWCGenerator.gea_base_dir,
                name=swc.name
            )

            tag_with_optional_value_4 = etree.SubElement(
                enviroment_variables, "TAG-WITH-OPTIONAL-VALUE")
            key = etree.SubElement(tag_with_optional_value_4, "KEY")
            key.text = "MACHINE"
            value = etree.SubElement(tag_with_optional_value_4, "VALUE")
            value.text = machine

            for env in swc.envs:
                tag_with_optional_value_ = etree.SubElement(
                    enviroment_variables, "TAG-WITH-OPTIONAL-VALUE")
                key = etree.SubElement(tag_with_optional_value_, "KEY")
                key.text = env.name
                value = etree.SubElement(tag_with_optional_value_, "VALUE")
                value.text = env.value

    @staticmethod
    def _generate_swc(swc: MFSWC, data: MFManifest, node: etree.Element, machine: str):
        package = etree.SubElement(node, "AR-PACKAGE")
        set_short_name(package, swc.name)
        elements = etree.SubElement(package, "ELEMENTS")

        # PROCESS-DESIGN
        process_design = etree.SubElement(elements, "PROCESS-DESIGN")
        set_short_name(process_design, swc.name + "ProcessDesign")
        exec_ref = etree.SubElement(process_design, "EXECUTABLE-REF")
        exec_ref.attrib["DEST"] = "EXECUTABLE"
        exec_ref.text = "/ai/momenta/swc/" + swc.name + "/" + swc.name + "Exec"

        # EXECUTABLE
        executable = etree.SubElement(elements, "EXECUTABLE")
        set_short_name(executable, swc.name + "Exec")
        root_sw_prototype = etree.SubElement(
            executable, "ROOT-SW-COMPONENT-PROTOTYPE")
        set_short_name(root_sw_prototype, swc.name + "Root")
        application_ref = etree.SubElement(
            root_sw_prototype, "APPLICATION-TYPE-TREF")
        application_ref.attrib["DEST"] = "ADAPTIVE-APPLICATION-SW-COMPONENT-TYPE"
        application_ref.text = "/ai/momenta/swc/" + swc.name + "/" + swc.name + "Swc"

        # ADAPTIVE-APPLICATION-SW-COMPONENT-TYPE
        ap_swc = etree.SubElement(
            elements, "ADAPTIVE-APPLICATION-SW-COMPONENT-TYPE")
        set_short_name(ap_swc, swc.name + "Swc")
        ports = etree.SubElement(ap_swc, "PORTS")
        sub_port_set = set()
        for sub_port in swc.sub_ports:
            target_topic = data.filter_topic(sub_port.topic_name)
            if (target_topic.datatype,
                    target_topic.huawei_ref.is_someip) in sub_port_set or "HUAWEI-MDC" not in target_topic.platforms:
                continue
            sub_port_set.add(
                (target_topic.datatype, target_topic.huawei_ref.is_someip))
            target_datatype = data.filter_datatype(target_topic.datatype)
            r_port_prototype = etree.SubElement(ports, "R-PORT-PROTOTYPE")
            set_short_name(r_port_prototype, swc.name + "Sub" + target_datatype.name + (
                "SomeIp" if target_topic.huawei_ref.is_someip else ""))
            interface_ref = etree.SubElement(
                r_port_prototype, "REQUIRED-INTERFACE-TREF")
            interface_ref.attrib["DEST"] = "SERVICE-INTERFACE"
            interface_ref.text = "/ai/momenta/service_interface/" + target_datatype.name + "ServiceInterface" + (
                "SomeIp" if target_topic.huawei_ref.is_someip else "")
        sub_port_set.clear()
        for sub_port in swc.sub_huawei_ports:
            if sub_port.datatype_name in sub_port_set:
                continue
            sub_port_set.add(sub_port.datatype_name)
            r_port_prototype = etree.SubElement(ports, "R-PORT-PROTOTYPE")
            set_short_name(r_port_prototype, swc.name + "Sub" +
                           sub_port.datatype_name.split("::")[-1])
            interface_ref = etree.SubElement(
                r_port_prototype, "REQUIRED-INTERFACE-TREF")
            interface_ref.attrib["DEST"] = "SERVICE-INTERFACE"
            interface_ref.text = sub_port.service_interface
        pub_port_set = set()
        for pub_port in swc.pub_ports:
            target_topic = data.filter_topic(pub_port.topic_name)
            if (target_topic.datatype,
                    target_topic.huawei_ref.is_someip) in pub_port_set or "HUAWEI-MDC" not in target_topic.platforms:
                continue
            pub_port_set.add(
                (target_topic.datatype, target_topic.huawei_ref.is_someip))
            target_datatype = data.filter_datatype(target_topic.datatype)
            p_port_prototype = etree.SubElement(ports, "P-PORT-PROTOTYPE")
            set_short_name(p_port_prototype, swc.name + "Pub" + target_datatype.name + (
                "SomeIp" if target_topic.huawei_ref.is_someip else ""))
            interface_ref = etree.SubElement(
                p_port_prototype, "PROVIDED-INTERFACE-TREF")
            interface_ref.attrib["DEST"] = "SERVICE-INTERFACE"
            interface_ref.text = "/ai/momenta/service_interface/" + target_datatype.name + "ServiceInterface" + (
                "SomeIp" if target_topic.huawei_ref.is_someip else "")
        pub_port_set.clear()
        for pub_port in swc.pub_huawei_ports:
            if pub_port.datatype_name in pub_port_set:
                continue
            pub_port_set.add(pub_port.datatype_name)
            p_port_prototype = etree.SubElement(ports, "P-PORT-PROTOTYPE")
            set_short_name(p_port_prototype, swc.name + "Pub" +
                           pub_port.datatype_name.split("::")[-1])
            interface_ref = etree.SubElement(
                p_port_prototype, "PROVIDED-INTERFACE-TREF")
            interface_ref.attrib["DEST"] = "SERVICE-INTERFACE"
            interface_ref.text = pub_port.service_interface

        # SERVICE-INSTANCE-TO-PORT-PROTOTYPE-MAPPING
        # Pub instances
        for instance in data.service_instances:
            if instance.sender_swc.name != swc.name or "HUAWEI-MDC" not in instance.topic.platforms:
                continue

            instance_prototype_mapping = etree.SubElement(
                elements, "SERVICE-INSTANCE-TO-PORT-PROTOTYPE-MAPPING")
            set_short_name(instance_prototype_mapping,
                           swc.name + "Pub" + instance.datatype.name + "Id" + str(instance.instance_id) + "Mapping")
            port_prototype_ref = etree.SubElement(
                instance_prototype_mapping, "PORT-PROTOTYPE-IREF")
            root_ref = etree.SubElement(
                port_prototype_ref, "CONTEXT-ROOT-SW-COMPONENT-PROTOTYPE-REF")
            root_ref.attrib["DEST"] = "ROOT-SW-COMPONENT-PROTOTYPE"
            root_ref.text = "/ai/momenta/swc/" + swc.name + \
                "/" + swc.name + "Exec/" + swc.name + "Root"
            target_port_ref = etree.SubElement(
                port_prototype_ref, "TARGET-PORT-PROTOTYPE-REF")
            target_port_ref.attrib["DEST"] = "P-PORT-PROTOTYPE"
            target_port_ref.text = "/ai/momenta/swc/" + swc.name + "/" + swc.name + "Swc/" + swc.name + "Pub" + \
                                   instance.datatype.name + \
                ("SomeIp" if instance.topic.huawei_ref.is_someip else "")
            process_ref = etree.SubElement(
                instance_prototype_mapping, "PROCESS-REF")
            process_ref.attrib["DEST"] = "PROCESS-DESIGN"
            process_ref.text = "/ai/momenta/swc/" + \
                swc.name + "/" + swc.name + "ProcessDesign"
            instance_ref = etree.SubElement(
                instance_prototype_mapping, "SERVICE-INSTANCE-REF")
            instance_ref.attrib[
                "DEST"] = "PROVIDED-SOMEIP-SERVICE-INSTANCE" if instance.topic.huawei_ref.is_someip else "DDS-PROVIDED-SERVICE-INSTANCE"
            instance_ref.text = "/ai/momenta/service_instance/" + instance.datatype.name + str(
                instance.instance_id) + "ProvidedInstanceBy" + instance.sender_swc.name + (
                "SomeIp" if instance.topic.huawei_ref.is_someip else "")
        # Sub instances
        for connection in data.connections:
            if connection.receiver_swc.name != swc.name or "HUAWEI-MDC" not in connection.instance.topic.platforms:
                continue
            is_in_same_domain = (
                connection.sender_swc.huawei_ref.is_in_aos_core == connection.receiver_swc.huawei_ref.is_in_aos_core)
            instance_prototype_mapping = etree.SubElement(
                elements, "SERVICE-INSTANCE-TO-PORT-PROTOTYPE-MAPPING")
            set_short_name(instance_prototype_mapping,
                           swc.name + "Sub" + connection.datatype.name + "Id" + str(
                               connection.instance.instance_id) + "Mapping")
            port_prototype_ref = etree.SubElement(
                instance_prototype_mapping, "PORT-PROTOTYPE-IREF")
            root_ref = etree.SubElement(
                port_prototype_ref, "CONTEXT-ROOT-SW-COMPONENT-PROTOTYPE-REF")
            root_ref.attrib["DEST"] = "ROOT-SW-COMPONENT-PROTOTYPE"
            root_ref.text = "/ai/momenta/swc/" + swc.name + \
                "/" + swc.name + "Exec/" + swc.name + "Root"
            target_port_ref = etree.SubElement(
                port_prototype_ref, "TARGET-PORT-PROTOTYPE-REF")
            target_port_ref.attrib["DEST"] = "R-PORT-PROTOTYPE"
            target_port_ref.text = "/ai/momenta/swc/" + swc.name + "/" + swc.name + "Swc/" + swc.name + "Sub" + \
                                   connection.instance.datatype.name + (
                                       "SomeIp" if connection.topic.huawei_ref.is_someip else "")
            process_ref = etree.SubElement(
                instance_prototype_mapping, "PROCESS-REF")
            process_ref.attrib["DEST"] = "PROCESS-DESIGN"
            process_ref.text = "/ai/momenta/swc/" + \
                swc.name + "/" + swc.name + "ProcessDesign"
            instance_ref = etree.SubElement(
                instance_prototype_mapping, "SERVICE-INSTANCE-REF")
            instance_ref.attrib[
                "DEST"] = "REQUIRED-SOMEIP-SERVICE-INSTANCE" if connection.topic.huawei_ref.is_someip else "DDS-REQUIRED-SERVICE-INSTANCE"
            if connection.topic.huawei_ref.is_someip:
                instance_ref.text = "/ai/momenta/service_instance/" + connection.instance.datatype.name + str(
                    connection.instance.instance_id) + "RequiredInstanceBy" + connection.instance.sender_swc.name + "SomeIp"
            else:
                instance_ref.text = "/ai/momenta/service_instance/" + connection.instance.datatype.name + str(
                    connection.instance.instance_id) + "RequiredInstanceBy" + connection.instance.sender_swc.name + (
                    "" if is_in_same_domain else "ICC")
        # Sub huawei ports
        for sub_port in swc.sub_huawei_ports:
            dt_name = sub_port.datatype_name.split("::")[-1]
            instance_prototype_mapping = etree.SubElement(
                elements, "SERVICE-INSTANCE-TO-PORT-PROTOTYPE-MAPPING")
            set_short_name(instance_prototype_mapping,
                           swc.name + "Sub" + dt_name + "Id" + sub_port.instance_id + "Mapping")
            port_prototype_ref = etree.SubElement(
                instance_prototype_mapping, "PORT-PROTOTYPE-IREF")
            root_ref = etree.SubElement(
                port_prototype_ref, "CONTEXT-ROOT-SW-COMPONENT-PROTOTYPE-REF")
            root_ref.attrib["DEST"] = "ROOT-SW-COMPONENT-PROTOTYPE"
            root_ref.text = "/ai/momenta/swc/" + swc.name + \
                "/" + swc.name + "Exec/" + swc.name + "Root"
            target_port_ref = etree.SubElement(
                port_prototype_ref, "TARGET-PORT-PROTOTYPE-REF")
            target_port_ref.attrib["DEST"] = "R-PORT-PROTOTYPE"
            target_port_ref.text = "/ai/momenta/swc/" + swc.name + \
                "/" + swc.name + "Swc/" + swc.name + "Sub" + dt_name
            process_ref = etree.SubElement(
                instance_prototype_mapping, "PROCESS-REF")
            process_ref.attrib["DEST"] = "PROCESS-DESIGN"
            process_ref.text = "/ai/momenta/swc/" + \
                swc.name + "/" + swc.name + "ProcessDesign"
            instance_ref = etree.SubElement(
                instance_prototype_mapping, "SERVICE-INSTANCE-REF")
            instance_ref.attrib["DEST"] = "DDS-REQUIRED-SERVICE-INSTANCE"
            instance_ref.text = "/ai/momenta/service_instance/" + \
                dt_name + sub_port.instance_id + "RequiredInstanceByHuawei"
        # Pub huawei ports
        for pub_port in swc.pub_huawei_ports:
            dt_name = pub_port.datatype_name.split("::")[-1]
            instance_prototype_mapping = etree.SubElement(
                elements, "SERVICE-INSTANCE-TO-PORT-PROTOTYPE-MAPPING")
            set_short_name(instance_prototype_mapping,
                           swc.name + "Pub" + dt_name + "Id" + pub_port.instance_id + "Mapping")
            port_prototype_ref = etree.SubElement(
                instance_prototype_mapping, "PORT-PROTOTYPE-IREF")
            root_ref = etree.SubElement(
                port_prototype_ref, "CONTEXT-ROOT-SW-COMPONENT-PROTOTYPE-REF")
            root_ref.attrib["DEST"] = "ROOT-SW-COMPONENT-PROTOTYPE"
            root_ref.text = "/ai/momenta/swc/" + swc.name + \
                "/" + swc.name + "Exec/" + swc.name + "Root"
            target_port_ref = etree.SubElement(
                port_prototype_ref, "TARGET-PORT-PROTOTYPE-REF")
            target_port_ref.attrib["DEST"] = "P-PORT-PROTOTYPE"
            target_port_ref.text = "/ai/momenta/swc/" + swc.name + \
                "/" + swc.name + "Swc/" + swc.name + "Pub" + dt_name
            process_ref = etree.SubElement(
                instance_prototype_mapping, "PROCESS-REF")
            process_ref.attrib["DEST"] = "PROCESS-DESIGN"
            process_ref.text = "/ai/momenta/swc/" + \
                swc.name + "/" + swc.name + "ProcessDesign"
            instance_ref = etree.SubElement(
                instance_prototype_mapping, "SERVICE-INSTANCE-REF")
            instance_ref.attrib["DEST"] = "DDS-PROVIDED-SERVICE-INSTANCE"
            instance_ref.text = "/ai/momenta/service_instance/" + dt_name + \
                pub_port.instance_id + "ProvidedInstanceBy" + swc.name

        # PROCESS
        process = etree.SubElement(elements, "PROCESS")
        set_short_name(process, swc.name + "Process")
        design_ref = etree.SubElement(process, "DESIGN-REF")
        design_ref.attrib["DEST"] = "PROCESS-DESIGN"
        design_ref.text = "/ai/momenta/swc/" + \
            swc.name + "/" + swc.name + "ProcessDesign"
        executable_ref = etree.SubElement(process, "EXECUTABLE-REF")
        executable_ref.attrib["DEST"] = "EXECUTABLE"
        executable_ref.text = "/ai/momenta/swc/" + swc.name + "/" + swc.name + "Exec"

        process_state_machine = etree.SubElement(
            process, "PROCESS-STATE-MACHINE")
        set_short_name(process_state_machine, swc.name + "ProcessState")
        type_tref = etree.SubElement(process_state_machine, "TYPE-TREF")
        type_tref.attrib["DEST"] = "MODE-DECLARATION-GROUP"
        type_tref.text = "/HuaweiMDC/ModeDeclaration/ProcessState"

        state_dependent_startup_configs = etree.SubElement(
            process, "STATE-DEPENDENT-STARTUP-CONFIGS")
        state_dependent_startup_config = etree.SubElement(state_dependent_startup_configs,
                                                          "STATE-DEPENDENT-STARTUP-CONFIG")

        if swc.dependencies:
            execution_dependencys = etree.SubElement(
                state_dependent_startup_config, "EXECUTION-DEPENDENCYS")
            for dep in swc.dependencies:
                execution_dependency = etree.SubElement(
                    execution_dependencys, "EXECUTION-DEPENDENCY")
                process_state_iref = etree.SubElement(
                    execution_dependency, "PROCESS-STATE-IREF")
                process_state_ref = etree.SubElement(
                    process_state_iref, "CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF")
                process_state_ref.attrib["DEST"] = "MODE-DECLARATION-GROUP-PROTOTYPE"
                process_state_ref.text = "/ai/momenta/swc/{swc}/{swc}Process/{swc}ProcessState".format(
                    swc=dep)
                target_mode_ref = etree.SubElement(
                    process_state_iref, "TARGET-MODE-DECLARATION-REF")
                target_mode_ref.attrib["DEST"] = "MODE-DECLARATION"
                target_mode_ref.text = "/HuaweiMDC/ModeDeclaration/ProcessState/Running"

        function_group_state_irefs = etree.SubElement(
            state_dependent_startup_config, "FUNCTION-GROUP-STATE-IREFS")
        function_group_state_iref = etree.SubElement(
            function_group_state_irefs, "FUNCTION-GROUP-STATE-IREF")
        target_mode_declaration_ref = etree.SubElement(
            function_group_state_iref, "TARGET-MODE-DECLARATION-REF")
        target_mode_declaration_ref.attrib["DEST"] = "MODE-DECLARATION"
        target_mode_declaration_ref.text = "/HuaweiMDC/ModeDeclaration/Access/Running"
        context_mode_declaration_group_prototype_ref = etree.SubElement(function_group_state_iref,
                                                                        "CONTEXT-MODE-DECLARATION-GROUP-PROTOTYPE-REF")
        context_mode_declaration_group_prototype_ref.attrib[
            "DEST"] = "MODE-DECLARATION-GROUP-PROTOTYPE"
        context_mode_declaration_group_prototype_ref.text = "/HuaweiMDC/{machine}Machine/{machine}Machine/Access".format(
            machine=machine)
        resource_group_ref = etree.SubElement(
            state_dependent_startup_config, "RESOURCE-GROUP-REF")
        resource_group_ref.attrib["DEST"] = "RESOURCE-GROUP"
        resource_group_ref.text = "/HuaweiMDC/{machine}Machine/{machine}Machine/OS/ResourceLimit".format(
            machine=machine)
        startup_config_ref = etree.SubElement(
            state_dependent_startup_config, "STARTUP-CONFIG-REF")
        startup_config_ref.attrib["DEST"] = "STARTUP-CONFIG"
        startup_config_ref.text = "/ai/momenta/em/StartupConfigSet/" + \
            swc.name + "StartupConfig"

    @staticmethod
    def generate(data: MFManifest, machine: str):
        doc, ar_package_momenta = generate_empty_arxml()
        ar_package_momenta_packages = etree.SubElement(
            ar_package_momenta, "AR-PACKAGES")
        ar_package_swc = etree.SubElement(
            ar_package_momenta_packages, "AR-PACKAGE")
        set_short_name(ar_package_swc, "swc")
        ar_package_swc_packages = etree.SubElement(
            ar_package_swc, "AR-PACKAGES")

        for swc in data.swcs:
            HuaweiAPSWCGenerator._generate_swc(
                swc, data, ar_package_swc_packages, machine)

        return etree.tostring(doc, xml_declaration=True, encoding="UTF-8", pretty_print=True)

    @staticmethod
    def generate_em(data: MFManifest, machine: str):
        doc, ar_package_momenta = generate_empty_arxml()
        ar_package_momenta_packages = etree.SubElement(
            ar_package_momenta, "AR-PACKAGES")
        ar_package_em = etree.SubElement(
            ar_package_momenta_packages, "AR-PACKAGE")
        set_short_name(ar_package_em, "em")

        HuaweiAPSWCGenerator._generate_em(data, ar_package_em, machine)

        return etree.tostring(doc, xml_declaration=True, encoding="UTF-8", pretty_print=True)
