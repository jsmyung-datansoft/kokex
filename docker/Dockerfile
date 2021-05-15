FROM python:3.7-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME=/kokex
ENV PORT=8081

RUN mkdir ${HOME}
WORKDIR ${HOME}

# install mecab
RUN apt-get update \
&& apt-get install apt-utils python3-dev curl gcc g++ make git tzdata -y
RUN ["/bin/bash", "-c", "bash <(curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh)"]

# install dependencies
COPY requirements.txt ${HOME}
RUN pip install --no-cache-dir -r requirements.txt

# install kokex
COPY kokex ${HOME}

EXPOSE ${PORT}
CMD uvicorn server.server:app --host 0.0.0.0 --port ${PORT}