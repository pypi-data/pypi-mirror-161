import glob
import os

from PyPDF2 import PdfFileMerger
from graphviz import Digraph
from loguru import logger

from mf_manifest_tools_simple.data_struct import MFManifest

__all__ = ["plot_topo_graph"]


def plot_topo_graph(data: MFManifest, output_path: str):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    g = Digraph(comment="MF", engine="dot")
    g.attr('node', shape="box")
    g.attr('graph', ratio="fill")
    groups = {"__DEFAULT__": []}
    for swc in data.swcs:
        if swc.group:
            if swc.group not in groups:
                groups[swc.group] = []
            groups[swc.group].append(swc)
        else:
            groups["__DEFAULT__"].append(swc)
    for group in groups:
        if group == "__DEFAULT__":
            for swc in groups[group]:
                g.node(swc.name)
        else:
            with g.subgraph(name="cluster_" + group) as sg:
                sg.attr(label=group)
                for swc in groups[group]:
                    sg.node(swc.name, fontsize="16")
    # Aggregate connections
    conns = {}
    for conn in data.connections:
        key = (conn.sender_swc.name, conn.receiver_swc.name)
        if key not in conns:
            conns[key] = []
        conns[key].append(conn.topic.topic_name)
    # for conn in conns:
    #     g.edge(conn[0], conn[1], r"\n".join(conns[conn]), fontsize="10")
    conned_list = []
    for conn in conns:
        if conn[0] == conn[1]:
            continue
        key = (conn[0], conn[1])
        if not key in conned_list:
            conned_list.append(key)

    edged_list = []
    for key in conned_list:
        if key not in edged_list:
            key_reverse = (key[1], key[0])
            edged_list.append(key)
            edged_list.append(key_reverse)
            if key_reverse in conned_list:
                g.edge(key[0], key[1], dir="both")
                conned_list.remove(key_reverse)
            else:
                g.edge(key[0], key[1])
                conned_list.remove(key)

    logger.info("Rendering to file {}", output_path + "/mf_plot.gv.pdf")
    g.unflatten().render(output_path + "/mf_plot.gv", view=False)
    logger.success("Done")
    plot_node_graph(data, output_path)
    merge_pdf(data, output_path)
    clean_middleware(output_path)


def plot_node_graph(data: MFManifest, output_path: str):
    for swc in data.swcs:
        g = Digraph(comment=swc.name, engine="dot")
        g.attr('node', shape="box")
        g.attr('graph', ratio="fill", ranksep="2")
        g.attr(rankdir='TD')
        sub_nodes = set()
        pub_nodes = set()
        conns = []
        g.node(swc.name)
        for conn in data.connections:
            topic_name = conn.topic.mfr_ref.mfr_topic
            topic_name = "\n/".join(topic_name.split('/')).lstrip()
            if conn.receiver_swc.name == swc.name:
                sub_nodes.add(conn.sender_swc.name)
                conns.append((conn.sender_swc.name + "_sub", swc.name, topic_name))
            elif conn.sender_swc.name == swc.name:
                pub_nodes.add(conn.receiver_swc.name)
                conns.append((swc.name, conn.receiver_swc.name + "_pub", topic_name))
        with g.subgraph(name="cluster_sub") as sub:
            sub.attr(label="sub", rank='same')
            for node in sub_nodes:
                sub.node(node + '_sub', node)
        with g.subgraph(name="cluster_pub") as pub:
            pub.attr(label="pub", rank='same')
            for node in pub_nodes:
                pub.node(node + '_pub', node)
        for conn in conns:
            g.edge(conn[0], conn[1], conn[2], fontsize="10")
        logger.info("Rendering topic to file {}", output_path + f"/{swc.name}.gv.pdf")
        g.unflatten().render(output_path + f"/{swc.name}.gv", view=False)
        logger.success("Done")


def merge_pdf(data: MFManifest, output_path: str):
    merger = PdfFileMerger()
    merger.append(open(output_path + "/mf_plot.gv.pdf", "rb"))
    merger.addBookmark("Overall", 0, parent=None)
    for i, swc in enumerate(data.swcs):
        merger.append(open(output_path + f"/{swc.name}.gv.pdf", "rb"))
        merger.addBookmark(swc.name, i + 1, parent=None)
    logger.info("Merging ", output_path + "/maf_manifest.pdf")
    merger.write(open(output_path + "/maf_manifest.pdf", "wb"))
    logger.success(f"Maf Manifest Topo Graph has been saved as {output_path}/maf_manifest.pdf")


def clean_middleware(output_path: str):
    fileList = glob.glob(output_path + "/*.gv*", recursive=False)
    for file in fileList:
        os.remove(file)
