# kokex

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/jsmyung-datansoft/kokex/Python%20package)
![GitHub](https://img.shields.io/github/license/jsmyung-datansoft/kokex)

한국어 문서 집합에서 키워드를 추출하는 라이브러리입니다. 
구문분석을 통해 사전 없이도 고유명사, 복합명사, 신조어에 강건한 키워드 추출기를 만들고자 합니다.

간단한 사용예는 아래와 같습니다.

```python
import kokex

keywords = kokex.keywords([
    '첫 번째 문서입니다. 여러 문장을 포함할 수 있습니다.',
    '두 번째 문서입니다. 여러 문서를 포함할 수 있습니다.'
])

print(keywords)  # {'번째': 2, '문서': 3, '문장': 1, '포함': 2}
```

## 설치
설치는 `pip` 를 이용하는 방법과 `docker-compose` 를 이용하는 방법이 있습니다.

#### pip

`pip install kokex`

이 라이브러리는 konlpy 와 Mecab 형태소 분석기에 의존성이 있습니다. 
konlpy 의 [설치 안내](https://konlpy.org/ko/v0.5.2/install) 에 따라 Mecab 을 설치해주시기 바랍니다. 예를 들어, Mac 환경에서는 아래의 명령을 입력하시기 바랍니다.

```
$ bash <(curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh)
```

#### docker-compose
도커 컴포즈가 있다면, 모든 의존성이 설치된 상태로 로컬 API 서버를 구동할 수 있습니다. 
이 저장소를 clone 한 후에 `bin/run_server.sh` 를 실행하세요.

`http://localhost:8081/docs` 에 접속하면 API 문서를 확인할 수 있습니다. 포트를 변경하고 싶다면 `.env.dev` 파일을 참고하세요.

서버를 실행하면 아래와 같이 http 요청을 처리할 수 있습니다.
```
curl -X POST \
  http://localhost:8081/keywords \
  -d '{
	"docs": [
		"첫 번째 문서입니다. 여러 문장을 포함할 수 있습니다.", 
		"두 번째 문서입니다. 여러 문서를 포함할 수 있습니다."
	]
}'
```

## 참여
API 에 대한 수정, 제안은 새로운 이슈 생성을 통해 시작해주세요.
모든 논의는 이슈의 댓글로 진행되면 좋겠습니다.

소스 코드를 수정한다면, `bin/run_test.sh` 를 실행하여 기존 테스트 문장의 분석 결과를 해치지 않도록 해야합니다.
만약 새로운 테스트 문장을 추가한다면, `test` 디렉토리의 파일에서 해당 문장과 결과를 업데이트하세요. 