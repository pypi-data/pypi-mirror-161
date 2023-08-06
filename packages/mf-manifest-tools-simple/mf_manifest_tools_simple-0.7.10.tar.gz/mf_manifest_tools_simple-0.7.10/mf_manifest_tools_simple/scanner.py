import os
from pathlib import Path

from loguru import logger

from mf_manifest_tools_simple.aggregator import ManifestAggregator
from mf_manifest_tools_simple.data_struct import MFManifest
from mf_manifest_tools_simple.exceptions import ManifestNotValid, NotMFManifest
from mf_manifest_tools_simple.parser import ManifestXMLParser, ManifestYAMLParser
from mf_manifest_tools_simple.validator import ManifestValidator


class ManifestScanner(object):
    @staticmethod
    def scan(path: str):
        if not os.path.exists(path) or not os.path.isdir(path):
            raise ManifestNotValid("Path to scan not exists")
        xml_files = sorted(list(Path(path).rglob("*.[xX][mM][lL]")))
        yaml_files = sorted(list(Path(path).rglob("*.[yY][mM][lL]")) + list(Path(path).rglob("*.[yY][aA][mM][lL]")))
        ret = MFManifest()
        # Parse each valid xml file into ret
        for xml_file in xml_files:
            if ".idea" in str(xml_file):
                continue
            try:
                parser = ManifestXMLParser(str(xml_file))
            except NotMFManifest:
                continue
            parser.parse_to_db(ret)
        for yaml_file in yaml_files:
            parser = ManifestYAMLParser(str(yaml_file))
            parser.parse_to_db(ret)
        # Validate
        ManifestValidator.validate(ret)
        # Aggregate
        ManifestAggregator.aggregate(ret)
        # Fro debug
        logger.debug("Connections:")
        for conn in ret.connections:
            logger.debug(conn)
        logger.debug("Service instances:")
        for ins in ret.service_instances:
            logger.debug(ins)
        return ret
