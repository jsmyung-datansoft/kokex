import sys
from os import environ, path
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
SERVER_PORT = int(environ.get("SERVER_PORT", 8081))

import kokex

app = FastAPI()


class KEXRequestKeywords(BaseModel):
    docs: List[str]


class KEXResponseKeywords(BaseModel):
    keywords: Dict[str, int]


@app.post("/keywords", response_model=KEXResponseKeywords)
def keywords(kex_request: KEXRequestKeywords):
    result = kokex.keywords(kex_request.docs)

    return JSONResponse(content=result)


class KEXRequestParse(BaseModel):
    doc: str
    debug: Optional[bool] = True


class KEXResponseParse(BaseModel):
    tree_str: str


@app.post("/parse", response_model=KEXResponseParse)
def parse(kex_request: KEXRequestParse):
    result = kokex.parse(kex_request.doc, debug=kex_request.debug)
    return JSONResponse(content=result)


if __name__ == "__main__":
    uvicorn.run("server:app", reload=True, host="0.0.0.0", port=SERVER_PORT)
