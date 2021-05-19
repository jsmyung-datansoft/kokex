import re

from konlpy.tag import Mecab

from .preproc import preproc
from .tree import NodeData, ParseTree


class DocumentParser:
    def __init__(self):
        self.document = ""
        self.morphs = []
        self.mecab = Mecab()

        # tree initialization
        self.tree = ParseTree()

    def parse(self, document):
        # preprocessing
        self.document = preproc(document)
        self.morphs = self._morphs_with_specialchars(self.document)

        # root 생성
        self.tree.clear()
        self.tree.add_node(
            node_id=ParseTree.ID_ROOT,
            node_data=NodeData(
                node_id=ParseTree.ID_ROOT,
                node_type="문서",
                org_txt_form=self.document,
                pos_txt_form=" ".join(
                    [f"{morph[0]}/{morph[1]}" for morph in self.morphs]
                ),
            ),
        )

        self._create_words()

    def _is_hanja(self, text):
        re_pattern = r"[\u2e80-\u2eff\u31c0-\u31ef\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fbf\uf900-\ufaff]"
        return re.match(pattern=re_pattern, string=text)

    # mecab이 공백/개행문자등을 걸러내서, 이를 보전하기 위한 유틸리티 함수
    def _morphs_with_specialchars(self, txt):
        old_morphs = self.mecab.pos(txt)
        new_morphs = []
        txt_idx = 0
        for morph, tag in old_morphs:
            morph_idx = 0

            # morph 에 해당하지 않는 문자열이 원문 텍스트에 있는 경우 추출
            start_txt_idx = txt_idx
            while txt[txt_idx] != morph[morph_idx]:
                txt_idx += 1
            end_txt_idx = txt_idx

            # morph 에 해당하는 문자열은 건너뜀
            while morph_idx < len(morph) and txt[txt_idx] == morph[morph_idx]:
                txt_idx += 1
                morph_idx += 1

            # 추출된 신규 형태소 추가
            if start_txt_idx < end_txt_idx:
                new_morphs.append(
                    (txt[start_txt_idx:end_txt_idx], "SWS")
                )  # 특수문자는 SWS 태그를 준다

            # 원래 morph도 신규로 추가
            new_morphs.append((morph, tag))

        return new_morphs

    ##### create_word 관련 함수 시작
    def _create_words(self):
        """Create word nodes from morphs"""
        words = self._words_from_morphs(self.morphs)

        for idx, word in enumerate(words):
            # org_txt, pos_txt 계산
            org_txt_form = ""
            pos_txt_form = ""
            for morph in word:
                org_txt_form += morph[0]
                pos_txt_form += morph[1] if len(pos_txt_form) == 0 else f"+{morph[1]}"
            pos_txt_form = f"{org_txt_form}/{pos_txt_form}"

            self.tree.add_node(
                node_id=f"{ParseTree.ID_ROOT}_{idx:03d}",
                node_data=NodeData(
                    node_id=f"{ParseTree.ID_ROOT}_{idx:03d}",
                    node_type="단어",
                    parent_node_id=ParseTree.ID_ROOT,
                    org_txt_form=org_txt_form,
                    pos_txt_form=pos_txt_form,
                ),
            )

        self._create_composite_words()
        self._create_josa_suffix_words()

    # 형태소 분석결과에서 구분자 태그를 이용해 단어를 추출한다.
    def _words_from_morphs(self, morphs):
        words = []
        word = []

        is_hashtag_mode = False
        is_single_quote_mode = False

        for morph in morphs:
            # hashtag 처리
            if not is_hashtag_mode and len(word) == 0 and morph[0] == "#":
                is_hashtag_mode = True

            if is_hashtag_mode:
                if morph[1] == "SWS":
                    if len(word) > 0:
                        txt, pos = map(list, zip(*word))
                        words.append([("".join(txt), "NNP")])
                        word = []
                    words.append([morph])  # 현재 morph는 delimiter 인데, 독립적인 단어로 만든다
                    is_hashtag_mode = False
                else:
                    if morph[0] == "#" and len(word) > 0:
                        txt, pos = map(list, zip(*word))
                        words.append([("".join(txt), "NNP")])
                        word = []

                    word.append(morph)

                continue

            # ''로 둘러싸인 짧은 문자열(10 형태소 이내)는 하나의 고유명사로 분류한다
            if not is_single_quote_mode and len(word) == 0 and morph[0] == "'":
                words.append([morph])
                is_single_quote_mode = True
                continue

            if is_single_quote_mode:
                if morph[0] == "'":
                    if len(word) > 0:
                        txt, pos = map(list, zip(*word))
                        words.append([("".join(txt), "NNP")])
                        word = []
                    words.append([morph])
                    is_single_quote_mode = False
                else:
                    word.append(morph)
                    if len(word) > 10:
                        for m in word:
                            words.append([m])
                        word = []
                        is_single_quote_mode = False
                continue

            # 외국어가 모두 대문자이면 고유명사로 처리한다
            if morph[1] == "SL" and morph[0].isupper() and len(morph[0]) > 1:
                morph = (morph[0], "NNP")

            # 일반적인 단어 처리
            words.append([morph])

        # for 문 이후 남은 형태소에 대해 word 처리
        if len(word) > 0:
            if is_hashtag_mode:
                txt, pos = map(list, zip(*word))
                words.append([("".join(txt), "NNP")])
            else:
                words.append(word)

        return words

    def _create_composite_words(self):
        delimiters = [
            "SF",
            "SE",
            "SSO",
            "SSC",
            "SC",
            "SY",
            "SWS",  # 기호/공백 문자로 구분
            "JKS",
            "JKC",
            "JKG",
            "JKO",
            "JKB",
            "JKV",
            "JKQ",
            "JX",
            "JC",  # 명사 추출을 위해 관계언을 살려둔다
            "IC",
            "UNKNOWN",  # 감탄사 활용
        ]
        node_ids = self.tree.get_children_node_ids(parent_node_id=ParseTree.ID_ROOT)

        idx = 0
        sub_nodes = []
        while idx < len(node_ids):
            node_data = self.tree.get_node_data_by_id(node_ids[idx])

            if node_data.get_last_pos_tag() in delimiters:
                if len(sub_nodes) > 1:
                    self._create_sub_tree(
                        parent_node_id=ParseTree.ID_ROOT,
                        children_node_data=sub_nodes,
                        node_type="단어",
                    )
                sub_nodes = []
                idx += 1
                continue

            sub_nodes.append(node_data)
            idx += 1

        if len(sub_nodes) > 1:
            self._create_sub_tree(
                parent_node_id=ParseTree.ID_ROOT,
                children_node_data=sub_nodes,
                node_type="단어",
            )

    def _create_josa_suffix_words(self):
        children_ids = self.tree.get_children_node_ids(parent_node_id=ParseTree.ID_ROOT)

        sub_nodes = []
        for idx, child_id in enumerate(children_ids):
            child_data = self.tree.get_node_data_by_id(children_ids[idx])
            sub_nodes.append(child_data)

            if child_data.get_last_pos_tag() == "SWS":
                sub_nodes = []
                continue
            if (
                child_data.get_last_pos_tag() == "SY"
                and len(child_data.org_txt_form) > 1
            ):
                if len(sub_nodes) > 0:
                    self._create_sub_tree(
                        parent_node_id=ParseTree.ID_ROOT,
                        children_node_data=sub_nodes,
                        node_type="단어",
                    )
                sub_nodes = []
                continue
            if child_data.word_tag == "관계언":
                self._create_sub_tree(
                    parent_node_id=ParseTree.ID_ROOT,
                    children_node_data=sub_nodes,
                    node_type="단어",
                )
                sub_nodes = []
                continue

    #### 유틸리티 함수 - 트리 분할 / 합병 관련
    def _update_sub_tree_identifier(
        self, sub_root_node_data, new_node_id, new_parent_node_id, updated_data
    ):
        children_node_ids = self.tree.get_children_node_ids(sub_root_node_data.node_id)

        for idx, child_id in enumerate(children_node_ids):
            child_data = self.tree.get_node_data_by_id(child_id)
            self._update_sub_tree_identifier(
                child_data, f"{new_node_id}_{idx:03d}", new_node_id, updated_data
            )

        self.tree.remove_node(sub_root_node_data.node_id)  # 기존 노드는 삭제
        sub_root_node_data.node_id = new_node_id  # 새로운 노드 ID를 부여
        sub_root_node_data.parent_node_id = new_parent_node_id
        updated_data.append(sub_root_node_data)  # 데이터를 유지하여 추후 다시 추가할 수 있도록 함

    def _create_sub_tree(self, parent_node_id, children_node_data, node_type=None):
        if len(children_node_data) > 0:
            # org_txt, pos_txt 계산
            org_txt_form = "".join([node.org_txt_form for node in children_node_data])
            pos_txt_form = " ".join([node.pos_txt_form for node in children_node_data])

            # 기존 node id 업데이트
            new_node_id = children_node_data[0].node_id
            updated_data = []
            for idx, node_data in enumerate(children_node_data):
                self._update_sub_tree_identifier(
                    node_data, f"{new_node_id}_{idx:03d}", new_node_id, updated_data
                )

            # 신규 node 생성
            self.tree.add_node(
                node_id=new_node_id,
                node_data=NodeData(
                    node_id=new_node_id,
                    node_type=node_type,
                    parent_node_id=parent_node_id,
                    org_txt_form=org_txt_form,
                    pos_txt_form=pos_txt_form,
                ),
            )

            # 기존 nodes 를 신규 node 하위로 이동
            for node_data in updated_data:
                self.tree.add_node(node_id=node_data.node_id, node_data=node_data)

    # 명사 추출 관련 함수 시작
    def condition_noun_candidates(self, x):
        node_data = self.tree.get_node_data_by_id(x)
        return (
            (node_data.node_type == "단어" and node_data.word_tag in ["체언", "독립언"])
            and (
                len(node_data.org_txt_form) > 1
                or self._is_hanja(node_data.org_txt_form)
            )
            and node_data.org_txt_form
            not in [
                # 불용어
            ]
        )

    def nouns(self):
        result = []

        # 1단어 체언
        for node_id in self.tree.filter_nodes(self.condition_noun_candidates):
            result.append(self.tree.get_node_data_by_id(node_id).org_txt_form)

        return result

    def printable_tree(self, debug=True):
        return self.tree.printable_subtree(
            sub_root_node_id=ParseTree.ID_ROOT, debug=debug
        )
