# kokex

![GitHub](https://img.shields.io/github/license/jsmyung-datansoft/kokex)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/jsmyung-datansoft/kokex/Python%20package)
[![Documentation Status](https://readthedocs.org/projects/kokex/badge/?version=latest)](https://kokex.readthedocs.io/ko/latest/?badge=latest)

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
더 자세한 사용법은 [문서](https://kokex.readthedocs.io/) 를 참고해주세요.

## 설치
설치는 `pip` 를 이용하는 방법과 `docker` 를 이용하는 방법이 있습니다.

#### pip

`pip install kokex`

이 라이브러리는 konlpy 와 Mecab 형태소 분석기에 의존성이 있습니다. 
konlpy 의 [설치 안내](https://konlpy.org/ko/v0.5.2/install) 에 따라 Mecab 을 설치해주시기 바랍니다. 예를 들어, Mac 환경에서는 아래의 명령을 입력하시기 바랍니다.

```
$ bash <(curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh)
```

#### docker
도커를 사용한다면, 모든 의존성이 설치된 상태로 로컬 API 서버를 구동할 수 있습니다.
```
export KOKEX_PORT=80
export KOKEX_VERSION=0.0.11

docker pull kokex/server:${KOKEX_VERSION}
docker run -d -p ${KOKEX_PORT}:8081 --name kokex-server --rm kokex/server:${KOKEX_VERSION}
```

서버를 종료할 때는 `docker stop kokex-server` 를 입력하세요.

서버를 실행하면 아래와 같이 http 요청을 처리할 수 있습니다.
```
curl -X POST \
  http://localhost/keywords \
  -d '{
	"docs": [
		"첫 번째 문서입니다. 여러 문장을 포함할 수 있습니다.", 
		"두 번째 문서입니다. 여러 문서를 포함할 수 있습니다."
	]
}'
```
그리고 `http://localhost/docs` 에 접속하면 API 문서를 확인할 수 있습니다. 

## 참여
모든 논의는 이슈를 통해 이루어지면 좋겠습니다.

#### API 사용자
kokex api 를 사용하는 분들이라면 새로운 문장에 대한 분석 요청을 하실 수 있습니다.
테스트 문장과 함께 원하는 분석결과를 담아 이슈를 생성하실 수 있도록 템플릿(test_suggest)을 준비해두었으니 참고해주세요.

#### API 개발자
kokex api 개발에 관심이 있으시다면, 이슈를 생성 후 논의를 진행하고, 수정한 사항을 PR 해주시면 됩니다.
소스 코드를 수정하신다면, isort 와 black 으로 포맷팅을 해주시기 바랍니다. 저장소 복제 후 아래와 같이 입력하시면 이를 자동으로 체크할 수 있습니다.

```
pip install -r requirements.txt
pre-commit install
```

그리고 `bin/run_test.sh` 를 실행하여 기존 테스트 문장의 분석 결과를 해치지 않도록 해야합니다.
테스트 문장은, `test` 디렉토리의 test_{API_NAME}.py 파일에서 찾아보실 수 있습니다. 