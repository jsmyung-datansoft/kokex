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
