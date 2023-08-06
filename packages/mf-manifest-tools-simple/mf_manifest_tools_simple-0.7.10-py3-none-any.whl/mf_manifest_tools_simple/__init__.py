import os
import sys

from docopt import docopt
from loguru import logger

from mf_manifest_tools_simple.data_struct import MFManifest
from mf_manifest_tools_simple.scanner import ManifestScanner

__version__ = "0.7.6"


def main():
    doc = """MF manifest tools

Usage:
  mf_manifest_tools_simple generate huawei_ap <manifest_dir> <output_dir> [--machine=<machine>] [--verbose]
  mf_manifest_tools_simple generate mfr <manifest_dir> <output_dir> [--verbose]
  mf_manifest_tools_simple generate motionwise <manifest_dir> <output_dir> [--verbose]
  mf_manifest_tools_simple generate mf_manifest <manifest_dir> <output_dir> [--verbose]
  mf_manifest_tools_simple validate <manifest_dir> [--verbose]
  mf_manifest_tools_simple plot <manifest_dir> <output_dir> [--verbose]
  mf_manifest_tools_simple generate_excel <manifest_dir> <maf_document_dir> <output_dir>
  mf_manifest_tools_simple hack huawei_datatype <manifest_file> [--verbose]
  mf_manifest_tools_simple hack huawei_camera <manifest_file> [--verbose]
  mf_manifest_tools_simple generate huawei_cmake <swc_name> <output_dir> [--conan] [--verbose]

Options:
  --conan  generate CMakeLists.txt with conan
  --verbose  Show debug log"""
    print(""" __  __ _____   __  __             _  __           _   
|  \/  |  ___| |  \/  | __ _ _ __ (_)/ _| ___  ___| |_ 
| |\/| | |_    | |\/| |/ _` | '_ \| | |_ / _ \/ __| __|
| |  | |  _|   | |  | | (_| | | | | |  _|  __/\__ \ |_ 
|_|  |_|_|     |_|  |_|\__,_|_| |_|_|_|  \___||___/\__|""")
    print(sys.argv[1:])
    arguments = docopt(doc, version=__version__)
    print(arguments)
    if arguments["--verbose"]:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.remove()
        logger.add(sys.stderr, level="INFO")
    logger.info("MF Manifest Tools -- Version " + __version__)

    data = None
    if arguments["<manifest_dir>"]:
        if not os.path.exists(arguments["<manifest_dir>"]) or not os.path.isdir(arguments["<manifest_dir>"]):
            logger.error("Manifest directory not valid")
            exit(-1)
        data = ManifestScanner.scan(arguments["<manifest_dir>"])

    if arguments["generate"] and arguments["huawei_ap"]:
        from mf_manifest_tools_simple.generators.huawei_ap import HuaweiAPGenerator
        HuaweiAPGenerator.generate(data, arguments["<output_dir>"], arguments["--machine"])
    elif arguments["generate"] and arguments["mfr"]:
        from mf_manifest_tools_simple.generators.mfr import MFRGenerator
        MFRGenerator.generate(data, arguments["<output_dir>"])
    elif arguments["generate"] and arguments["motionwise"]:
        logger.error("Motionwise generator not implemented yet")
        exit(-1)
    elif arguments["validate"]:
        # Done by scanner
        logger.success("Validation passed")
    elif arguments["plot"]:
        from mf_manifest_tools_simple.plot import plot_topo_graph
        plot_topo_graph(data, arguments["<output_dir>"])
    elif arguments["generate_excel"]:
        from mf_manifest_tools_simple.generators.excel import ExcelGenerator
        ExcelGenerator.generate(data, arguments["<maf_document_dir>"], arguments["<output_dir>"])
    elif arguments["hack"]:
        if arguments["huawei_datatype"]:
            from mf_manifest_tools_simple.hackers import hack_huawei_data_type
            hack_huawei_data_type(arguments["<manifest_file>"])
        elif arguments["huawei_camera"]:
            from mf_manifest_tools_simple.hackers import hack_huawei_camera
            hack_huawei_camera(arguments["<manifest_file>"])
    elif arguments["generate"] and arguments["huawei_cmake"]:
        from mf_manifest_tools_simple.generators.huawei_ap import HuaweiAPCmakeGenerator
        HuaweiAPCmakeGenerator.generate(arguments["<swc_name>"], arguments["<output_dir>"], arguments["--conan"])
    elif arguments["generate"] and arguments["mf_manifest"]:
        from mf_manifest_tools_simple.generators.mf_manifest import MFManifestGenerator
        MFManifestGenerator.generate(data, arguments["<output_dir>"])
