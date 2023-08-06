from lxml import etree

__all__ = ["hack_huawei_camera"]


def hack_huawei_camera(filepath: str):
    data = etree.parse(filepath)
    nsmap = {"a": "http://autosar.org/schema/r4.0"}
    refs = data.xpath("//a:EVENT-REF", namespaces=nsmap)
    for ref in refs:
        name = ref.text.split("/")
        if name[-2] in ["CameraEncodedMbufServiceInterface", "CameraDecodedMbufServiceInterface"]:
            name[-1] = "mdcEvent"
            ref.text = "/".join(name)
    types = data.xpath("//a:VARIABLE-DATA-PROTOTYPE/a:SHORT-NAME", namespaces=nsmap)
    for t in types:
        interface_name = t.getparent().getparent().getparent().xpath("./a:SHORT-NAME", namespaces=nsmap)[0].text
        if interface_name == "CameraEncodedMbufServiceInterface":
            ns = t.getparent().getparent().getparent().xpath("./a:NAMESPACES/a:SYMBOL-PROPS", namespaces=nsmap)
            ns[-1].xpath("./a:SHORT-NAME", namespaces=nsmap)[0].text = "camera_encoded"
            ns[-1].xpath("./a:SYMBOL", namespaces=nsmap)[0].text = "camera_encoded"
            t.text = "mdcEvent"
        elif interface_name == "CameraDecodedMbufServiceInterface":
            t.text = "mdcEvent"
    f = open(filepath, "wb")
    f.write(etree.tostring(data, xml_declaration=True, encoding="UTF-8", pretty_print=True))
    f.close()
