from typing import Dict, List
from mf_manifest_tools_simple.data_struct import MFSWC, MFDataType, MFManifest, MFTopic
import re


class MFManifestSearcher:
    def __init__(self, data: MFManifest):
        self.data = data

    def searchTopic(self, keyword: str, is_regex=True) -> List[MFTopic]:
        if not keyword:
            return []

        matcher = None
        if is_regex:
            matcher = re.compile(keyword)

        res = []
        for topic in self.data.topics:
            if is_regex and (matcher.match(topic.topic_name) or matcher.match(topic.mfr_ref.mfr_topic)):
                res.appned(topic)
            elif (not is_regex) and (keyword in topic.topic_name or keyword in topic.mfr_ref.mfr_topic):
                res.append(topic)
        return res

    def searchDatatype(self, keyword: str, is_regex=True) -> List[MFDataType]:
        if not keyword:
            return []

        matcher = None
        if is_regex:
            matcher = re.compile(keyword)

        res = []
        for dt in self.data.datatypes:
            if is_regex and (matcher.match(dt.name) or matcher.match(dt.c_ref.file) or matcher.match(dt.c_ref.struct)):
                res.appned(dt)
            elif (not is_regex) and (keyword in dt.name or keyword in dt.c_ref.file or keyword in dt.c_ref.struct):
                res.append(dt)
        return res

    def searchSWC(self, keyword: str, is_regex=True) -> List[MFSWC]:
        if not keyword:
            return []

        matcher = None
        if is_regex:
            matcher = re.compile(keyword)

        res = []
        for swc in self.data.swcs:
            if is_regex and matcher.match(swc.name):
                res.appned(swc)
            elif not is_regex and keyword in swc.name:
                res.append(swc)
        return res

    def getSWCByTopic(self, topic_name) -> Dict:
        if not topic_name:
            return []

        res = {"subers": [], "pubers": []}
        for swc in self.data.swcs:
            for sub_port in swc.sub_ports:
                if sub_port.topic_name == topic_name:
                    res["subers"].append(swc)
                    break
            for pub_port in swc.pub_ports:
                if pub_port.topic_name == topic_name:
                    res["pubers"].append(swc)
                    break
        return res

    def getTopicByDatatype(self, datatype_name) -> List[MFDataType]:
        if not datatype_name:
            return []

        res = []
        for topic in self.data.topics:
            if topic.datatype.name == datatype_name:
                res.append(topic)
        return res
