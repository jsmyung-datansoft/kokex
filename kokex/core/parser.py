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

        self._identify_sub_documents()
        self._identify_sentences()

        self._identify_phrases()
        self._identify_clauses()

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

    ##### identify_sub_document 관련 함수 시작
    def _identify_sub_documents(self):
        children_node_ids = self.tree.get_children_node_ids(
            parent_node_id=ParseTree.ID_ROOT
        )

        sub_nodes = []
        is_sub_document = False
        for idx, child_node_id in enumerate(children_node_ids):
            child_node_data = self.tree.get_node_data_by_id(children_node_ids[idx])

            if not is_sub_document and 1 in map(
                lambda x: 1 if child_node_data.org_txt_form.find(x) > -1 else 0,
                ['"', "“"],
            ):
                is_sub_document = True
                sub_nodes.append(child_node_data)
                continue

            if is_sub_document and 1 in map(
                lambda x: 1 if child_node_data.org_txt_form.find(x) > -1 else 0,
                ['"', "”"],
            ):
                sub_nodes.append(child_node_data)
                self._create_sub_tree(
                    parent_node_id=ParseTree.ID_ROOT,
                    children_node_data=sub_nodes,
                    node_type="문서",
                )
                sub_nodes = []
                is_sub_document = False
                continue

            if is_sub_document:
                sub_nodes.append(child_node_data)

    def _identify_sentences(self):
        def is_document_node_processed(tree, node_id):
            return tree.get_node_data_by_id(node_id).node_type == "문장"

        def get_not_processed_document_node_id(tree):
            for node_id in tree.filter_nodes(
                lambda x: tree.get_node_data_by_id(x).node_type == "문서"
            ):
                if 1 not in map(
                    lambda x: 1 if is_document_node_processed(tree, x) else 0,
                    tree.get_children_node_ids(parent_node_id=node_id),
                ):
                    return node_id
            return None

        document_node_id = get_not_processed_document_node_id(self.tree)
        while document_node_id:
            children_node_ids = self.tree.get_children_node_ids(
                parent_node_id=document_node_id
            )

            sub_nodes = []
            idx = 0
            while idx < len(children_node_ids):
                child_node_data = self.tree.get_node_data_by_id(children_node_ids[idx])

                # 문장의 처음에 공백문자를 추가하지 않는다
                if len(sub_nodes) == 0 and child_node_data.get_last_pos_tag() == "SWS":
                    idx += 1
                    continue

                sub_nodes.append(child_node_data)

                if child_node_data.node_type != "단어":
                    idx += 1
                    continue

                # 종결어미, 문장부호(.!?)로 문장구분
                if child_node_data.get_last_pos_tag() in ["EF", "SF"]:
                    idx += 1
                    while idx < len(children_node_ids):
                        next_child_node_data = self.tree.get_node_data_by_id(
                            children_node_ids[idx]
                        )
                        if next_child_node_data.get_last_pos_tag() in [
                            "SF",
                            "SE",
                            "SY",
                            "SWS",
                        ]:
                            sub_nodes.append(next_child_node_data)
                        else:
                            if sub_nodes[-1].get_last_pos_tag() in ["SWS"]:
                                sub_nodes = sub_nodes[0:-1]  # 공백으로 끝나지 않도록 조정한다
                            self._create_sub_tree(
                                parent_node_id=document_node_id,
                                children_node_data=sub_nodes,
                                node_type="문장",
                            )
                            sub_nodes = []
                            sub_nodes.append(next_child_node_data)
                            break

                        idx += 1

                # 종결부호 [.!?]/SY 후 띄어쓰기나 엔터가 오는 문장 처리
                elif (
                    child_node_data.org_txt_form[-1] in [".", "!", "?"]
                    and len(child_node_data.org_txt_form) == 1
                    and child_node_data.get_last_pos_tag() in ["SY"]
                ):
                    next_idx = idx + 1
                    if next_idx < len(children_node_ids):
                        next_child_node_data = self.tree.get_node_data_by_id(
                            children_node_ids[next_idx]
                        )
                        if next_child_node_data.get_last_pos_tag() in ["SWS"]:
                            self._create_sub_tree(
                                parent_node_id=document_node_id,
                                children_node_data=sub_nodes,
                                node_type="문장",
                            )
                            sub_nodes = []
                            idx = next_idx

                # 2개이상의 기호가 연속으로 왔을때 문장으로 구분함
                elif (
                    child_node_data.get_last_pos_tag() in ["SY"]
                    and len(child_node_data.org_txt_form) > 1
                ):
                    idx += 1
                    while idx < len(children_node_ids):
                        next_child_node_data = self.tree.get_node_data_by_id(
                            children_node_ids[idx]
                        )
                        if next_child_node_data.get_last_pos_tag() in [
                            "SY",
                            "SF",
                            "SE",
                        ]:
                            sub_nodes.append(next_child_node_data)
                        else:
                            self._create_sub_tree(
                                parent_node_id=document_node_id,
                                children_node_data=sub_nodes,
                                node_type="문장",
                            )
                            sub_nodes = []
                            sub_nodes.append(next_child_node_data)
                            break

                        idx += 1

                # 말줄임표로 구분된 문장 처리
                elif child_node_data.get_last_pos_tag() in ["SE"]:
                    self._create_sub_tree(
                        parent_node_id=document_node_id,
                        children_node_data=sub_nodes,
                        node_type="문장",
                    )
                    sub_nodes = []

                # 감탄사로 구분된 문장 처리
                elif child_node_data.get_last_pos_tag() in ["IC"]:
                    idx += 1
                    while idx < len(children_node_ids):
                        next_child_node_data = self.tree.get_node_data_by_id(
                            children_node_ids[idx]
                        )
                        if next_child_node_data.get_last_pos_tag() in ["IC", "SWS"]:
                            sub_nodes.append(next_child_node_data)
                        else:
                            if sub_nodes[-1].get_last_pos_tag() in ["SWS"]:
                                sub_nodes = sub_nodes[0:-1]  # 공백으로 끝나지 않도록 조정한다
                            self._create_sub_tree(
                                parent_node_id=document_node_id,
                                children_node_data=sub_nodes,
                                node_type="문장",
                            )
                            sub_nodes = []
                            sub_nodes.append(next_child_node_data)
                            break

                        idx += 1

                idx += 1

            if len(sub_nodes) > 0:
                self._create_sub_tree(
                    parent_node_id=document_node_id,
                    children_node_data=sub_nodes,
                    node_type="문장",
                )
            document_node_id = get_not_processed_document_node_id(self.tree)

    def _identify_phrases(self):
        def is_sentence_node_processed(tree, node_id):
            return tree.get_node_data_by_id(node_id).node_type == "구"

        def get_not_processed_sentence_node_id(tree):
            for node_id in tree.filter_nodes(
                lambda x: tree.get_node_data_by_id(x).node_type == "문장"
            ):
                if 1 not in map(
                    lambda x: 1 if is_sentence_node_processed(tree, x) else 0,
                    tree.get_children_node_ids(parent_node_id=node_id),
                ):
                    return node_id
            return None

        sentence_node_id = get_not_processed_sentence_node_id(self.tree)
        while sentence_node_id:
            children_node_ids = self.tree.get_children_node_ids(
                parent_node_id=sentence_node_id
            )

            sub_nodes = []
            idx = 0
            while idx < len(children_node_ids):
                child_node_data = self.tree.get_node_data_by_id(children_node_ids[idx])

                # 구의 처음에 공백문자를 추가하지 않는다
                if len(sub_nodes) == 0 and child_node_data.get_last_pos_tag() == "SWS":
                    idx += 1
                    continue

                sub_nodes.append(child_node_data)

                if child_node_data.node_type != "단어":
                    idx += 1
                    continue

                # 기본적으로 문장의 주성분 (주어, 목적어, 서술어, 보어)일 때 구를 구분한다
                if child_node_data.sentence_tag in ["주어", "목적어", "서술어", "보어"]:

                    # 목적어 뒤에 오는 관형어를 처리한다: '중국을 방문한 대통령'을 '중국을 방문한' '대통령' 으로 나눈다
                    if child_node_data.sentence_tag in ["목적어"]:
                        idx, sub_nodes = self.check_phrase_to_merge_next_word(
                            idx,
                            sub_nodes,
                            children_node_ids,
                            lambda next_node: next_node.sentence_tag in ["관형어"],
                        )

                    # 서술어 뒤어 오는 보조 용언 VX를 처리한다: '논란을 빚고 있다' 를 '논란을' '빚고 있다' 로 나눈다
                    if child_node_data.sentence_tag in ["서술어"]:
                        idx, sub_nodes = self.check_phrase_to_merge_next_word(
                            idx,
                            sub_nodes,
                            children_node_ids,
                            lambda next_node: next_node.get_first_pos_tag() in ["VX"],
                        )

                    # 동사(VV)로 시작하는 보어가 다음에 서술어를 만나면 합친다: '이긴것이 아니다', '위해서도 낫다'
                    if child_node_data.sentence_tag in [
                        "보어"
                    ] and child_node_data.get_first_pos_tag() in ["VV"]:
                        idx, sub_nodes = self.check_phrase_to_merge_next_word(
                            idx,
                            sub_nodes,
                            children_node_ids,
                            lambda next_node: next_node.sentence_tag in ["서술어"],
                        )

                    # 구 노드를 생성한다
                    self._create_sub_tree(
                        parent_node_id=sentence_node_id,
                        children_node_data=sub_nodes,
                        node_type="구",
                    )
                    sub_nodes = []

                idx += 1

            if len(sub_nodes) > 0:
                self._create_sub_tree(
                    parent_node_id=sentence_node_id,
                    children_node_data=sub_nodes,
                    node_type="구",
                )
            sentence_node_id = get_not_processed_sentence_node_id(self.tree)

    def check_phrase_to_merge_next_word(self, idx, sub_nodes, children_node_ids, rule):
        next_idx = idx + 1
        next_sub_nodes = []
        while next_idx < len(children_node_ids):
            next_child_node_data = self.tree.get_node_data_by_id(
                children_node_ids[next_idx]
            )
            if next_child_node_data.get_last_pos_tag() in ["SWS"]:  # 공백문자를 건너뛴다
                next_sub_nodes.append(next_child_node_data)
                next_idx += 1
                continue
            else:
                break

        if next_idx < len(children_node_ids):
            next_child_node_data = self.tree.get_node_data_by_id(
                children_node_ids[next_idx]
            )
            if rule(next_child_node_data):
                sub_nodes += next_sub_nodes
                sub_nodes.append(next_child_node_data)
                idx = next_idx

        return idx, sub_nodes

    def _identify_clauses(self):
        pass

    ##### 유틸리티 함수 - 트리 분할 / 합병 관련
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

    ##### 명사 추출 관련 함수 시작
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

    ##### 문장 분리 관련 함수 시작
    def sentences(self):
        result = []
        for node_id in self.tree.filter_nodes(
            lambda x: self.tree.get_node_data_by_id(x).node_type == "문장"
        ):
            node_data = self.tree.get_node_data_by_id(node_id)
            result.append(node_data.org_txt_form)
        return result

    def printable_tree(self, debug=True):
        return self.tree.printable_subtree(
            sub_root_node_id=ParseTree.ID_ROOT, debug=debug
        )
