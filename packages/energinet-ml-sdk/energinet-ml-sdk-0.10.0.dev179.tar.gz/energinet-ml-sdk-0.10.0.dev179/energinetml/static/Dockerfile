FROM python:3.9-slim

ARG MODEL_PATH
ARG OUTPUTS_PATH
ARG MODEL_VERSION

ENV MODEL_VERSION ${MODEL_VERSION}
ENV OUTPUTS_PATH ${OUTPUTS_PATH}

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y apt-transport-https
RUN pip3 install --upgrade wheel pip

COPY . /model

WORKDIR /model
RUN pip3 install -r requirements.txt

EXPOSE 80

WORKDIR ${MODEL_PATH}

CMD energinetml model serve --host 0.0.0.0 --port 80 --outputs-path "/model/${OUTPUTS_PATH}" --model-version ${MODEL_VERSION}
