FROM python:3.9-slim-buster

RUN apt update && apt install -y gcc libpq-dev

WORKDIR /mentor_notifier

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .