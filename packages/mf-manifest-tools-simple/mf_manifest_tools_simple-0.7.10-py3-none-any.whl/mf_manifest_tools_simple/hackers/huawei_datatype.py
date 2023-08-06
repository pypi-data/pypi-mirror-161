from lxml import etree

__all__ = ["hack_huawei_data_type"]


def hack_huawei_data_type(filepath: str):
    data = etree.parse(filepath)
    nsmap = {"a": "http://autosar.org/schema/r4.0"}
    hacklist = ["bool", "double", "float", "int16_t", "int32_t", "int64_t",
                "int8_t", "uint16_t", "uint32_t", "uint64_t", "uint8_t", "String"]
    datatypes = data.xpath("//a:STD-CPP-IMPLEMENTATION-DATA-TYPE", namespaces=nsmap)
    for datatype in datatypes:
        t = datatype.xpath("./a:SHORT-NAME", namespaces=nsmap)[0].text
        # if t in hacklist:
            # ns = etree.SubElement(datatype, "NAMESPACES")
            # symbol_props = etree.SubElement(ns, "SYMBOL-PROPS")
            # short_name = etree.SubElement(symbol_props, "SHORT-NAME")
            # short_name.text = "huawei"
            # symbol = etree.SubElement(symbol_props, "SYMBOL")
            # symbol.text = "huawei"
        if t == "String":
            dt = etree.SubElement(datatype.getparent(), "STD-CPP-IMPLEMENTATION-DATA-TYPE")
            short_name = etree.SubElement(dt, "SHORT-NAME")
            short_name.text = "StringVector"
            cate = etree.SubElement(dt, "CATEGORY")
            cate.text = "VECTOR"
            ns = etree.SubElement(dt, "NAMESPACES")
            symbol_props = etree.SubElement(ns, "SYMBOL-PROPS")
            s = etree.SubElement(symbol_props, "SHORT-NAME")
            s.text = "huawei"
            sym = etree.SubElement(symbol_props, "SYMBOL")
            sym.text = "huawei"
            tmp = etree.SubElement(dt, "TEMPLATE-ARGUMENTS")
            arg = etree.SubElement(tmp, "CPP-TEMPLATE-ARGUMENT")
            ref = etree.SubElement(arg, "TEMPLATE-TYPE-REF")
            ref.text = "/HuaweiMDC/StdCppDataType/String"
            ref.attrib["DEST"] = "STD-CPP-IMPLEMENTATION-DATA-TYPE"
    f = open(filepath, "wb")
    f.write(etree.tostring(data, xml_declaration=True, encoding="UTF-8", pretty_print=True))
    f.close()
