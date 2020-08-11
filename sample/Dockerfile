FROM ubuntu:18.04

RUN apt-get update -y
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y

RUN pip3 install --upgrade pip
RUN pip3 install requests

COPY ./src /app
WORKDIR /app

CMD python3 app.py
