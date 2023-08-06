from typing import Tuple

from lxml import etree

__all__ = ["set_short_name", "generate_empty_arxml"]


def set_short_name(node: etree.Element, name: str):
    short_name = etree.SubElement(node, "SHORT-NAME")
    short_name.text = name


def generate_empty_arxml() -> Tuple[etree.Element, etree.Element]:
    qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
    doc = etree.Element("{http://autosar.org/schema/r4.0}AUTOSAR",
                        {qname: "http://autosar.org/schema/r4.0 AUTOSAR_00048.xsd"},
                        nsmap={None: "http://autosar.org/schema/r4.0"})
    ar_packages = etree.SubElement(doc, "AR-PACKAGES")
    ar_package_ai = etree.SubElement(ar_packages, "AR-PACKAGE")
    set_short_name(ar_package_ai, "ai")
    ar_package_ai_packages = etree.SubElement(ar_package_ai, "AR-PACKAGES")
    ar_package_momenta = etree.SubElement(ar_package_ai_packages, "AR-PACKAGE")
    set_short_name(ar_package_momenta, "momenta")
    return doc, ar_package_momenta
