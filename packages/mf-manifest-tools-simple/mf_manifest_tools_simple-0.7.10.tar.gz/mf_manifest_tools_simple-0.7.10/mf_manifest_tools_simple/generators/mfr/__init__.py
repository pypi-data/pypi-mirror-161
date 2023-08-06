import os

from loguru import logger

from mf_manifest_tools_simple.data_struct import MFManifest
from mf_manifest_tools_simple.generators.mfr.connections import MFRConnectionsGenerator

__all__ = ["MFRGenerator"]


class MFRGenerator(object):
    @staticmethod
    def generate(data: MFManifest, output_path: str):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        if not os.path.isdir(output_path):
            raise Exception("Output path should be a directory")
        logger.info("Generating MFR connections")
        open(output_path + "/mfr_connections.yaml", "w").write(MFRConnectionsGenerator.generate(data))
        logger.success("MFR connections generated successfully")
