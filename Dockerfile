FROM ubuntu:18.04

RUN apt-get update -y
RUN apt-get install python3 -y
RUN apt-get install tzdata -y
RUN apt-get install python3-pip -y

RUN cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime
RUN echo "Asia/Seoul" > /etc/timezone
RUN pip3 install --upgrade pip
RUN pip3 install Flask
RUN pip3 install requests
RUN pip3 install jsonschema
RUN pip3 install pytest
RUN pip3 install cryptography
RUN pip3 install pymysql
RUN pip3 install pyyaml

ENV PYTHONIOENCODING = utf-8
ENV PYTHONPATH="/app/layers"

RUN apt-get install curl -y
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
RUN apt-get update && apt-get install google-cloud-sdk -y
RUN apt-get install kubectl -y
RUN apt-get install vim -y

COPY ./src /app
WORKDIR /app

CMD gcloud auth activate-service-account ${GCLOUD_SERVICE_ACCOUNT} --key-file=${GCLOUD_AUTH_PATH} --project=${GCLOUD_PROJECT_NAME}; python3 app.py

