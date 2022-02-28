FROM python:3.9-slim-buster

RUN apt update && apt install -y gcc libpq-dev

WORKDIR /mentor_notifier

COPY . .

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8888"]