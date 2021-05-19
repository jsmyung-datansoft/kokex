from collections import defaultdict
from typing import Dict, List

from kokex.core.parser import DocumentParser


def keywords(docs: List[str]) -> Dict[str, int]:
    """
    문서 목록을 받아서 포함된 키워드를 리턴합니다

    :param docs: 문서 목록
    :return: 키워드와 빈도가 담긴 딕셔너리
    """
    result = defaultdict(int)
    parser = DocumentParser()

    for doc in docs:
        parser.parse(document=doc)

        for noun in parser.nouns():
            result[noun] += 1

    return result


def parse(doc: str, debug: bool = True):
    """
    문서를 입력받아서 파싱된 결과를 문자열로 리턴합니다

    :param doc: 입력 문서
    :param debug: true 일 경우 문서위계, 5언 7성분 9품사 정보를 함께 출력 (기본값 true)
    :return: 출력을 위해 들여쓰기가 된 문자열
    """
    parser = DocumentParser()
    parser.parse(doc)

    return parser.printable_tree(debug=debug)
