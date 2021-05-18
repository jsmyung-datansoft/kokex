FROM kokex/server-base:0.1.0

# set environment variables
ENV HOME=/kokex
ENV PORT=8081

RUN mkdir ${HOME}
WORKDIR ${HOME}

# install dependencies
COPY requirements.txt ${HOME}
RUN apt-get update \
&& apt-get install apt-utils python3-dev curl gcc g++ make git tzdata -y \
&& pip install --no-cache-dir -r requirements.txt

# install kokex
COPY kokex ${HOME}

EXPOSE ${PORT}
CMD uvicorn server.server:app --host 0.0.0.0 --port ${PORT}