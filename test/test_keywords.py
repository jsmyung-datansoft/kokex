from fastapi.testclient import TestClient

import kokex
from kokex.server import server

client = TestClient(server.app)


def test_keywords_0001():
    check_results(
        input_documents=[
            "첫 번째 문서입니다. 여러 문장을 포함할 수 있습니다.",
            "두 번째 문서입니다. 여러 문서를 포함할 수 있습니다.",
        ],
        expected_results={"번째": 2, "문서": 3, "문장": 1, "포함": 2},
    )


def test_keywords_0002():
    check_results(
        input_documents=[
            "새로운 테스트 문장을 일련번호와 함께 메소드로 추가합니다.",
        ],
        expected_results={
            "테스트": 1,
            "문장": 1,
            "일련번호": 1,
            "일련": 1,
            "번호": 1,
            "메소드": 1,
            "추가": 1,
        },
    )


def check_results(input_documents, expected_results):
    keywords = kokex.keywords(input_documents)
    assert keywords == expected_results

    response = client.post("/keywords", json={"docs": input_documents})
    assert response.status_code == 200
    assert response.json() == expected_results
