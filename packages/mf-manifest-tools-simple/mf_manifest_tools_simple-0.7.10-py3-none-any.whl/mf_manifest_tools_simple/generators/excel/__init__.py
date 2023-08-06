import os

from loguru import logger

from mf_manifest_tools_simple.data_struct import MFManifest
from mf_manifest_tools_simple.generators.excel.excel_worker import ExcelReader

__all__ = ["ExcelGenerator"]


class ExcelGenerator(object):
    @staticmethod
    def generate(data: MFManifest, doxygen_dir: str, output_path: str):
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        SWCS = []
        for swc in data.swcs:
            SWC = {
                "name": "",
                "topics": [],
                "data_type": [],
                "hyper_link": [],
                "input_swcs": [],
                "input_value_range": [],
                "input_rte_api": [],
                "out_topics": [],
                "out_data_type": [],
                "out_hyper_link": [],
                "output_swcs": [],
                "output_value_range": [],
                "output_rte_api": [],
                "complementary_msg": None
            }
            subs = swc.sub_ports
            SWC["name"] = swc.name
            # 根据swc name去读取配置文件，来填充空白部分
            SWC["complementary_msg"] = swc.complementary
            SWC["function_description"] = swc.function_description
            SWC["cpu_usage"] = swc.cpu_usage
            SWC["memory_usage"] = swc.memory_usage
            topic_names = [x.topic_name for x in subs]
            for target_topic in topic_names:
                for topic in data.topics:
                    if topic.topic_name == target_topic:
                        for sender in topic.senders:
                            SWC["input_swcs"].append(sender.name)
                            SWC["data_type"].append(topic.datatype)
                            mfr_topic = topic.mfr_ref.mfr_topic
                            if len(mfr_topic):
                                SWC["topics"].append(mfr_topic)
                            else:
                                SWC["topics"].append('(' + topic.topic_name + ')')
                            c_struct = data.filter_datatype(topic.datatype).c_ref.struct
                            SWC["hyper_link"].append("struct" + c_struct.split("::")[0].replace("_",
                                                                                                "__") + "_1_1" +
                                                     c_struct.split("::")[1] + ".html")
                            # SWC["input_value_range"].append(data.filter_datatype(topic.datatype).value_range)
                            SWC["input_rte_api"].append(topic.motionwise_ref.rte)

            pubs = swc.pub_ports
            out_topic_names = [x.topic_name for x in pubs]
            for target_topic in out_topic_names:
                output_swcs_ = []
                for topic in data.topics:
                    if topic.topic_name == target_topic:
                        for sender in topic.senders:
                            if sender.name == swc.name:
                                # SWC["output_value_range"].append(topic.value_range)
                                SWC["output_rte_api"].append(topic.motionwise_ref.rte)
                                SWC["out_data_type"].append(topic.datatype)
                                mfr_topic = topic.mfr_ref.mfr_topic
                                if len(mfr_topic):
                                    SWC["out_topics"].append(mfr_topic)
                                else:
                                    SWC["out_topics"].append('(' + topic.topic_name + ')')
                                c_struct = data.filter_datatype(topic.datatype).c_ref.struct
                                SWC["out_hyper_link"].append("struct" + c_struct.split("::")[0].replace("_",
                                                                                                        "__") + "_1_1" +
                                                             c_struct.split("::")[1] + ".html")
                                for swc_ in data.swcs:
                                    if topic.topic_name in [x.topic_name for x in swc_.sub_ports]:
                                        output_swcs_.append(swc_.name)
                                SWC["output_swcs"].append(';\n'.join(output_swcs_))

            SWCS.append(SWC)
        for swc in SWCS:
            logger.info("Generating excel document for {}".format(swc["name"]))
            ExcelReader(os.path.join(os.path.realpath(os.path.join(os.path.realpath(__file__), "..")), "template.xlsx"),
                        [swc], swc["name"], doxygen_dir, output_path)
        logger.success("Excel document generated successfully")
