from loguru import logger

from mf_manifest_tools_simple.data_struct import MFManifest, MFConnection, MFServiceInstance
from mf_manifest_tools_simple.exceptions import ManifestNotValid

__all__ = ["ManifestAggregator"]


class ManifestAggregator(object):
    service_interface_id_counter = 6000

    @staticmethod
    def aggregate(data: MFManifest):
        logger.info("Aggregating")
        custom_interface_id = set()
        for datatype in data.datatypes:
            if datatype.huawei_ref.interface_id != -1:
                custom_interface_id.add(datatype.huawei_ref.interface_id)
        for datatype in data.datatypes:
            if datatype.huawei_ref.interface_id == -1:
                while ManifestAggregator.service_interface_id_counter in custom_interface_id:
                    ManifestAggregator.service_interface_id_counter += 1
                datatype.huawei_ref.interface_id = ManifestAggregator.service_interface_id_counter
                ManifestAggregator.service_interface_id_counter += 1
            datatype_used = False
            for topic in data.topics:
                if topic.datatype == datatype.name:
                    datatype_used = True
                    break
            if not datatype_used:
                logger.warning("Datatype {} never used", datatype.name)
        for swc in data.swcs:
            for sub_port in swc.sub_ports:
                data.filter_topic(sub_port.topic_name).receivers.append(swc)
            for pub_port in swc.pub_ports:
                data.filter_topic(pub_port.topic_name).senders.append(swc)
            for dep in swc.dependencies:
                if data.filter_swc(dep) is None:
                    raise ManifestNotValid("SWC {} has invalid depencency {}".format(swc.name, dep))
        instance_counter = {}
        for topic in data.topics:
            # Check if topic is used
            topic_used = False
            for swc in data.swcs:
                for port in swc.sub_ports:
                    if port.topic_name == topic.topic_name:
                        topic_used = True
                        break
                if topic_used:
                    break
                for port in swc.pub_ports:
                    if port.topic_name == topic.topic_name:
                        topic_used = True
                        break
                if topic_used:
                    break
            if not topic_used:
                logger.warning("Topic {} never used", topic.topic_name)
            for subscriber in topic.receivers:
                for publisher in topic.senders:
                    instance = data.filter_service_instance(publisher.name, topic.topic_name, topic.datatype)
                    if instance is None:
                        if topic.datatype not in instance_counter:
                            instance_counter[topic.datatype] = set()
                            instance_counter[topic.datatype].add((publisher.name, topic.topic_name))
                        elif (publisher.name, topic.topic_name) not in instance_counter[topic.datatype]:
                            instance_counter[topic.datatype].add((publisher.name, topic.topic_name))
                        else:
                            raise Exception("Unknown exception")
                        instance_id = len(instance_counter[topic.datatype])
                        instance = MFServiceInstance(instance_id, publisher, topic,
                                                     data.filter_datatype(topic.datatype))
                        data.service_instances.append(instance)
                    data.connections.append(
                        MFConnection(publisher, subscriber, topic, data.filter_datatype(topic.datatype), instance))
        for complementary in data.complementaries:
            swc = data.filter_swc(complementary.name)
            if swc is not None:
                swc.complementary = complementary
        logger.success("Aggregator summary: {} Connections, {} instances", len(data.connections),
                       len(data.service_instances))
