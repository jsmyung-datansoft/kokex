from fastapi.testclient import TestClient

import kokex
from kokex.server import server

client = TestClient(server.app)


def test_sentences_0001():
    check_results(
        input_document="첫 번째 문서입니다. 여러 문장을 포함할 수 있습니다.",
        expected_results=["첫 번째 문서입니다.", "여러 문장을 포함할 수 있습니다."],
    )


def check_results(input_document, expected_results):
    sentences = kokex.sentences(input_document)
    assert sentences == expected_results

    response = client.post("/sentences", json={"doc": input_document})
    assert response.status_code == 200
    assert response.json() == expected_results
