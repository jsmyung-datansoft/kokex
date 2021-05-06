import html
import re


# preprocessing 함수
def preproc(document):
    document = _html_unescape(document)
    document = _replace_html_tag(document)
    document = _replace_url_link(document)
    document = _replace_email(document)
    document = _replace_mention(document)
    document = _replace_dots(document)
    document = _replace_kkks(document)
    document = _replace_unicode_char(document)
    return document


def _html_unescape(text):
    return html.unescape(text)


def _replace_html_tag(text):
    re_pattern = r"</?[a-zA-Z][a-zA-Z0-9]*>"
    return re.sub(pattern=re_pattern, repl="", string=text)


def _replace_url_link(text):
    re_pattern = r"(http|ftp|https)://(?:[-\w.]|(?:[%/\w]))+(\?.+?=.+?(&.+?=.+?)*\b)?"
    return re.sub(pattern=re_pattern, repl="", string=text)


def _replace_email(text):
    re_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    return re.sub(pattern=re_pattern, repl="", string=text)


def _replace_mention(text):
    re_pattern = r"@[a-zA-Z0-9_.+-]+"
    return re.sub(pattern=re_pattern, repl="", string=text)


def _replace_unicode_char(text):
    u_chars = "".join(
        re.findall(pattern=r"(\\u[0-9a-zA-Z]{4}|\\x[0-9a-zA-Z]{2})", string=repr(text))
    )
    return re.sub(pattern=fr"[{u_chars}]", repl=" ", string=text) if u_chars else text


def _replace_dots(text):
    re_pattern = r"((·{2,})|(\.{2,}))"
    return re.sub(pattern=re_pattern, repl="… ", string=text)


def _replace_kkks(text):
    re_pattern = r"(ㅋ{3,})"
    return re.sub(pattern=re_pattern, repl="ㅋㅋㅋ ", string=text)
