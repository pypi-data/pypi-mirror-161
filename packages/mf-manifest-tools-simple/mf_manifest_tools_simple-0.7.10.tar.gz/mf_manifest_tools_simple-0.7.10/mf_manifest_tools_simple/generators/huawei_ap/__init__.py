import os

from loguru import logger

from mf_manifest_tools_simple.data_struct import MFManifest
from mf_manifest_tools_simple.generators.huawei_ap.cmake import HuaweiAPCmakeGenerator
from mf_manifest_tools_simple.generators.huawei_ap.exec import HuaweiAPExecGenerator
from mf_manifest_tools_simple.generators.huawei_ap.service_instance import HuaweiAPServiceInstanceGenerator
from mf_manifest_tools_simple.generators.huawei_ap.service_interface import HuaweiAPServiceInterfaceGenerator
from mf_manifest_tools_simple.generators.huawei_ap.swc import HuaweiAPSWCGenerator
from mf_manifest_tools_simple.generators.huawei_ap.swc_datatypes import HuaweiAPSWCDatatypesGenerator

__all__ = ["HuaweiAPGenerator", "HuaweiAPCmakeGenerator"]


class HuaweiAPGenerator(object):
    @staticmethod
    def generate(data: MFManifest, output_path: str, machine: str):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        if not os.path.isdir(output_path):
            raise Exception("Output path should be a directory")
        if machine is None:
            machine = "Host0Dp"
            logger.info("Use default machine Host0Dp")
        logger.info("Generating Huawei AP service interface")
        open(output_path + "/service_interface.arxml",
             "wb").write(HuaweiAPServiceInterfaceGenerator.generate(data))
        logger.info("Generating Huawei AP service instance")
        open(output_path + "/service_instance.arxml", "wb").write(
            HuaweiAPServiceInstanceGenerator.generate(data, machine))
        logger.info("Generating Huawei AP swc")
        open(output_path + "/swc.arxml",
             "wb").write(HuaweiAPSWCGenerator.generate(data, machine))
        open(output_path + "/em.arxml",
             "wb").write(HuaweiAPSWCGenerator.generate_em(data, machine))
        logger.info("Generating Huawei AP swc datatypes")
        open(output_path + "/swc_datatypes.json",
             "wb").write(HuaweiAPSWCDatatypesGenerator.generate(data))
        logger.success("Huawei AP ARXMLs generated successfully")
        logger.info("Generating Huawei C++ snippets")
        cpp_path = os.path.join(output_path, "cpp")
        if not os.path.exists(cpp_path):
            os.makedirs(cpp_path)
        HuaweiAPExecGenerator.generate(data, cpp_path)
        logger.success("Huawei AP C++ snippets generated successfully")
