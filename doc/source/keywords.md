# Keywords

```python
import kokex

keywords = kokex.keywords([
    '첫 번째 문서입니다. 여러 문장을 포함할 수 있습니다.',
    '두 번째 문서입니다. 여러 문서를 포함할 수 있습니다.'
])

print(keywords)  # {'번째': 2, '문서': 3, '문장': 1, '포함': 2}
```