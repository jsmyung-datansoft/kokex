import sys
from os import environ, path
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
SERVER_PORT = int(environ.get("SERVER_PORT", 8081))

import kokex

app = FastAPI()
templates = Jinja2Templates(directory="template")


class KEXRequestKeywords(BaseModel):
    docs: List[str]


class KEXResponseKeywords(BaseModel):
    keywords: Dict[str, int]


@app.post("/keywords", response_model=KEXResponseKeywords)
def keywords(kex_request: KEXRequestKeywords):
    result = kokex.keywords(kex_request.docs)
    return JSONResponse(content=result)


class KEXRequestSentences(BaseModel):
    doc: str


class KEXResponseSentences(BaseModel):
    sentences: List[str]


@app.post("/sentences", response_model=KEXResponseSentences)
def sentences(kex_request: KEXRequestSentences):
    result = kokex.sentences(kex_request.doc)
    return JSONResponse(content=result)


@app.get("/parse", response_class=HTMLResponse)
def parse(request: Request):
    return templates.TemplateResponse("parse.html", {"request": request, "result": ""})


@app.post("/parse", response_class=HTMLResponse)
def parse(request: Request, doc: str = Form(...)):
    result = kokex.parse(doc, debug=True)
    result = result.replace("\n", "<br>")
    result = result.replace("\t", "&nbsp;" * 4)
    return templates.TemplateResponse(
        "parse.html", {"request": request, "doc": doc, "result": result}
    )


if __name__ == "__main__":
    uvicorn.run("server:app", reload=True, host="0.0.0.0", port=SERVER_PORT)
