import re

import networkx as nx


class NodeData:
    def __init__(
        self,
        node_id,
        node_type,
        parent_node_id=None,
        word_tag=None,
        sentence_tag=None,
        semantic_tag=None,
        org_txt_form=None,
        pos_txt_form=None,
    ):

        self.__node_id = node_id
        self.__node_type = node_type
        self.__parent_node_id = parent_node_id

        self.__word_tag = word_tag
        self.__sentence_tag = sentence_tag
        self.__semantic_tag = semantic_tag

        self.__org_txt_form = org_txt_form
        self.__pos_txt_form = pos_txt_form

    @property
    def node_id(self):
        return self.__node_id

    @node_id.setter
    def node_id(self, value):
        self.__node_id = value

    @property
    def node_type(self):
        return self.__node_type

    @node_type.setter
    def node_type(self, value):
        self.__node_type = value

    @property
    def parent_node_id(self):
        return self.__parent_node_id

    @parent_node_id.setter
    def parent_node_id(self, value):
        self.__parent_node_id = value

    @property
    def word_tag(self):
        return self.__word_tag

    @word_tag.setter
    def word_tag(self, value):
        self.__word_tag = value

    @property
    def sentence_tag(self):
        return self.__sentence_tag

    @sentence_tag.setter
    def sentence_tag(self, value):
        self.__sentence_tag = value

    @property
    def semantic_tag(self):
        return self.__semantic_tag

    @semantic_tag.setter
    def semantic_tag(self, value):
        self.__semantic_tag = value

    @property
    def org_txt_form(self):
        return self.__org_txt_form

    @org_txt_form.setter
    def org_txt_form(self, value):
        self.__org_txt_form = value

    @property
    def pos_txt_form(self):
        return self.__pos_txt_form

    @pos_txt_form.setter
    def pos_txt_form(self, value):
        self.__pos_txt_form = value

    def get_last_pos_tag(self):
        p = re.compile(r"(?<=[/+])[A-Z0-9_]+$")
        return p.findall(self.pos_txt_form)[0]

    def get_first_pos_tag(self):
        p = re.compile(r"(?<=/)[A-Z0-9_]+")
        return p.findall(self.pos_txt_form)[0]


class ParseTree:
    ID_ROOT = "root"

    def __init__(self):
        self.g = nx.DiGraph()
        self.root = None

    def clear(self):
        self.g.clear()
        self.root = None

    def add_node(self, node_id: str, node_data: NodeData):
        # ?????? ??????
        self.g.add_node(node_id, data=node_data)

        # ?????? ????????? ???????????? ?????? ????????? ?????? ??????
        if node_data.parent_node_id:
            self.g.add_edge(node_data.parent_node_id, node_id)

        # ????????? ????????? ?????? ?????????: 5??? 7????????? ??????
        if node_data.node_type in ["??????", "???"]:
            node_data.word_tag = self._compute_word_tag(node_data.get_last_pos_tag())
        if node_data.node_type in ["??????", "???", "???"]:
            node_data.sentence_tag = self._compute_sentence_tag(
                node_data.get_last_pos_tag()
            )

    def get_node_data_by_id(self, node_id: str):
        return self.g.nodes[node_id]["data"]

    def get_children_node_ids(self, parent_node_id: str):
        return sorted(self.g.adj[parent_node_id])

    def remove_node(self, node_id: str):
        self.g.remove_node(node_id)

    def filter_nodes(self, func):
        return filter(func, self.g.nodes)

    def is_leaf(self, node_id: str):
        return len(self.g.adj[node_id]) == 0

    def printable_subtree(self, sub_root_node_id, debug=True):
        node_depth = len(sub_root_node_id.split("_")) - 1
        node_data = self.g.nodes[sub_root_node_id]["data"]
        printable = ("\t" * node_depth) + "[" + node_data.node_id + "] "
        if debug:
            printable += (
                "["
                + node_data.node_type
                + "] "
                + "["
                + (node_data.word_tag if node_data.word_tag else "")
                + "] "
                + "["
                + (node_data.sentence_tag if node_data.sentence_tag else "")
                + "] "
                + node_data.pos_txt_form
            )
        else:
            printable += node_data.org_txt_form
        printable += "\n"

        for child_id in self.get_children_node_ids(sub_root_node_id):
            printable += self.printable_subtree(child_id, debug=debug)

        return printable

    # ?????? ?????? ?????? ?????????????????? ??????
    @staticmethod
    def _compute_word_tag(last_pos_tag: str):
        # 5??? ??????
        if last_pos_tag[0] == "N" or last_pos_tag in ["ETN", "XPN", "XSN", "SH"]:
            word_tag = "??????"
        elif last_pos_tag[0] == "V" or last_pos_tag in ["EP", "EF", "EC", "XSV", "XSA"]:
            word_tag = "??????"
        elif last_pos_tag[0] == "M" or last_pos_tag in ["ETM"]:
            word_tag = "?????????"
        elif last_pos_tag[0] == "J" or last_pos_tag in []:
            word_tag = "?????????"
        else:
            word_tag = "?????????"

        return word_tag

    @staticmethod
    def _compute_sentence_tag(last_pos_tag: str):
        # 7?????? ??????
        if last_pos_tag in ["JKS"]:
            sentence_tag = "??????"
        elif last_pos_tag in ["EP", "EF", "EC", "ETN"]:
            sentence_tag = "?????????"
        elif last_pos_tag in ["JKO"]:
            sentence_tag = "?????????"
        elif last_pos_tag in ["JX", "JKC"]:
            sentence_tag = "??????"
        elif last_pos_tag in ["JKB", "MAG"]:
            sentence_tag = "?????????"
        elif last_pos_tag in ["ETM", "JKG", "MM"]:
            sentence_tag = "?????????"
        else:
            sentence_tag = "?????????"

        return sentence_tag
