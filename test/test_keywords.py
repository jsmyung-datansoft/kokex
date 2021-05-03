import kokex


def test_keywords_0001():
    keywords = kokex.keywords([
        '첫 번째 문서입니다. 여러 문장을 포함할 수 있습니다.',
        '두 번째 문서입니다. 여러 문서를 포함할 수 있습니다.'
    ])

    assert keywords['번째'] == 2 and keywords['문서'] == 3 and keywords['문장'] == 1 and keywords['포함'] == 2


def test_keywords_0002():
    keywords = kokex.keywords([
        '새로운 테스트 문장을 일련번호와 함께 메소드로 추가합니다.',
    ])

    assert keywords['테스트'] == 1 and keywords['문장'] == 1 and keywords['일련번호'] == 1 and keywords['일련'] == 1 and \
        keywords['번호'] == 1 and keywords['메소드'] == 1 and keywords['추가'] == 1
